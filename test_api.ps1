$baseUrl = "http://localhost:5000/api"
$token = ""

function ApiCall($method, $path, $body) {
    $headers = @{}
    if ($token) { $headers["Authorization"] = "Bearer $token" }
    $params = @{Uri="$baseUrl$path";Method=$method;Headers=$headers;ContentType="application/json";UseBasicParsing=$true}
    if ($body) { $params["Body"] = ($body | ConvertTo-Json) }
    try {
        $r = Invoke-WebRequest @params
        Write-Host ">>> $method $path => $($r.StatusCode)" -ForegroundColor Green
        return ($r.Content | ConvertFrom-Json)
    } catch {
        Write-Host ">>> $method $path => $($_.Exception.Response.StatusCode.value__) ERROR" -ForegroundColor Red
        $reader = [System.IO.StreamReader]::new($_.Exception.Response.GetResponseStream())
        Write-Host $reader.ReadToEnd() -ForegroundColor Red
        return $null
    }
}

Write-Host "=== 1. LOGIN ===" -ForegroundColor Cyan
$login = ApiCall "POST" "/auth/login" @{email="admin@gdpbzn.bg";password="admin123"}
if ($login) { $token = $login.token; Write-Host "TOKEN: $($token.Substring(0,20))..." -ForegroundColor Yellow }

Write-Host "`n=== 2. GET CURRENT USER ===" -ForegroundColor Cyan
ApiCall "GET" "/auth/me"

Write-Host "`n=== 3. LIST INCIDENT TYPES ===" -ForegroundColor Cyan
$types = ApiCall "GET" "/incidents/types"
Write-Host "Types count: $($types.incident_types.Count)"

Write-Host "`n=== 4. CREATE INCIDENT ===" -ForegroundColor Cyan
$incident = ApiCall "POST" "/incidents" @{
    incident_type_id=1
    address="ul. Tzarigradsko Shose 150"
    city="Sofia"
    region="Sofia-city"
    latitude=42.6977
    longitude=23.3219
    description="Building fire in progress"
    priority=1
    team_ids=@(1,2)
}
$incidentId = $incident.incident.id
Write-Host "Created incident #$($incident.incident.incident_number), ID: $incidentId"

Write-Host "`n=== 5. LIST INCIDENTS ===" -ForegroundColor Cyan
ApiCall "GET" "/incidents"

Write-Host "`n=== 6. GET INCIDENT DETAIL ===" -ForegroundColor Cyan
ApiCall "GET" "/incidents/$incidentId"

Write-Host "`n=== 7. UPDATE INCIDENT STATUS ===" -ForegroundColor Cyan
ApiCall "PUT" "/incidents/$incidentId" @{status="on_scene"}

Write-Host "`n=== 8. LIST TEAMS ===" -ForegroundColor Cyan
$teams = ApiCall "GET" "/teams"
Write-Host "Teams count: $($teams.teams.Count)"

Write-Host "`n=== 9. GET AVAILABLE MEMBERS ===" -ForegroundColor Cyan
ApiCall "GET" "/teams/available-members"

Write-Host "`n=== 10. UPDATE TEAM STATUS ===" -ForegroundColor Cyan
ApiCall "PUT" "/incidents/$incidentId/teams/1" @{status="en_route"}

Write-Host "`n=== 11. CREATE TASK ===" -ForegroundColor Cyan
$task = ApiCall "POST" "/tasks" @{
    incident_id=$incidentId
    title="Deliver water tanker to scene"
    description="Need additional water supply"
    task_type="logistics"
    priority=1
    assigned_user_ids=@(2,3)
}
$taskId = $task.task.id
Write-Host "Created task ID: $taskId"

Write-Host "`n=== 12. LIST TASKS FOR INCIDENT ===" -ForegroundColor Cyan
ApiCall "GET" "/tasks/incident/$incidentId"

Write-Host "`n=== 13. GET MY TASKS ===" -ForegroundColor Cyan
ApiCall "GET" "/tasks/my"

Write-Host "`n=== 14. CHAT: GET CHANNEL ===" -ForegroundColor Cyan
$channel = ApiCall "GET" "/chat/channels/$incidentId"
$channelId = $channel.channel.id

Write-Host "`n=== 15. CHAT: SEND MESSAGE ===" -ForegroundColor Cyan
ApiCall "POST" "/chat/messages" @{channel_id=$channelId;content="Alpha team en route to location.";message_type="text"}

Write-Host "`n=== 16. CHAT: LIST MESSAGES ===" -ForegroundColor Cyan
ApiCall "GET" "/chat/messages/$channelId"

Write-Host "`n=== 17. CHAT: LIST TEMPLATES ===" -ForegroundColor Cyan
ApiCall "GET" "/chat/templates"

Write-Host "`n=== 18. MAP: CREATE MARKER ===" -ForegroundColor Cyan
ApiCall "POST" "/map/$incidentId/markers" @{
    marker_type="fire_front"
    label="Fire front north side"
    latitude=42.6980
    longitude=23.3220
    color="red"
}

Write-Host "`n=== 19. MAP: LIST MARKERS ===" -ForegroundColor Cyan
ApiCall "GET" "/map/$incidentId/markers"

Write-Host "`n=== 20. MAP: UPDATE FIRE FRONT ===" -ForegroundColor Cyan
ApiCall "PUT" "/map/$incidentId/fire-front" @{
    fire_front_coords=@(@(42.698,23.322),@(42.699,23.323))
    wind_direction="NE"
    wind_speed=15.5
}

Write-Host "`n=== 21. RESOURCES: LIST ===" -ForegroundColor Cyan
ApiCall "GET" "/resources"

Write-Host "`n=== 22. RESOURCES: CREATE RESOURCE ===" -ForegroundColor Cyan
$res = ApiCall "POST" "/resources" @{name="Water tanker 10kl";resource_type="water";quantity_available=10000;unit="liters"}
$resId = $res.resource.id

Write-Host "`n=== 23. RESOURCES: REQUEST ===" -ForegroundColor Cyan
ApiCall "POST" "/resources/requests" @{incident_id=$incidentId;resource_id=$resId;quantity=5000;notes="Urgent water supply needed"}

Write-Host "`n=== 24. RESOURCES: LIST REQUESTS ===" -ForegroundColor Cyan
ApiCall "GET" "/resources/requests/$incidentId"

Write-Host "`n=== 25. NOTIFICATIONS: LIST ===" -ForegroundColor Cyan
$notifs = ApiCall "GET" "/notifications"
Write-Host "Notifications count: $($notifs.notifications.Count)"

Write-Host "`n=== 26. ADD HAZARDOUS MATERIAL ===" -ForegroundColor Cyan
ApiCall "POST" "/incidents/$incidentId/hazardous-materials" @{hazardous_material_id=1}

Write-Host "`n=== 27. CREATE ACTION PLAN ===" -ForegroundColor Cyan
ApiCall "POST" "/incidents/$incidentId/action-plans" @{
    title="Fire suppression plan"
    description="Initial attack plan"
    steps=@(@{order=1;action="Size up the scene";assigned_to="All teams"},@{order=2;action="Establish water supply";assigned_to="Team 1"},@{order=3;action="Attack fire from north side";assigned_to="Team 2"})
    priority=1
}

Write-Host "`n=== 28. GET INCIDENT LOG ===" -ForegroundColor Cyan
$log = ApiCall "GET" "/incidents/$incidentId/log"
Write-Host "Log entries: $($log.logs.Count)"

Write-Host "`n=== 29. LIST FIRE TRUCKS ===" -ForegroundColor Cyan
ApiCall "GET" "/teams/fire-trucks"

Write-Host "`n=== 30. LIST SHIFTS ===" -ForegroundColor Cyan
ApiCall "GET" "/teams/shifts"

Write-Host "`n=== ALL TESTS COMPLETE ===" -ForegroundColor Cyan
