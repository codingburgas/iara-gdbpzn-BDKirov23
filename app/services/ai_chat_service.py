import re
import random
from app.models.chat import ChatTemplate
from app.models.incident import Incident, IncidentType
from app.models.team import Team
from app.models.resource import Resource
from app.services.ai_provider import AIProvider


class AIChatService:
    def __init__(self):
        self.conversations = {}

    def get_response(self, user_id, message, incident_id=None):
        message_lower = message.lower().strip()

        real_response = AIProvider.ask_ai(message, user_id)
        if real_response:
            return real_response

        context = self._detect_context(message_lower)
        response = self._generate_response(context, message_lower, incident_id)

        return response

    def _detect_context(self, message):
        topics = {
            "greeting": ["hi", "hello", "здравей", "здрасти", "hey", "привет", "добър ден"],
            "help": ["help", "помощ", "какво можеш", "какво правиш", "как работи"],
            "incident_stats": ["колко инцидент", "брой произшествия", "активни пожари", "статистика"],
            "incident_create": ["създай произшествие", "нов инцидент", "регистрирай пожар", "добави инцидент"],
            "team_info": ["кой екип", "налични екипи", "свободни екипи", "екип"],
            "resource_info": ["какви ресурси", "наличност", "ресурси", "вода", "гориво", "пяна"],
            "status_info": ["статус", "какво става", "актуална", "положение"],
            "weather": ["време", "вятър", "температура", "климат"],
            "procedures": ["процедура", "правилник", "как да", "как се", "инструкция"],
            "emergency": ["авария", "спешно", "бързо", "извънредно", "опасно"],
            "farewell": ["bye", "чао", "довиждане", "merci", "благодаря", "ok"],
        }

        for topic, keywords in topics.items():
            if any(kw in message for kw in keywords):
                return topic
        return "general"

    def _generate_response(self, context, message, incident_id=None):
        responses = {
            "greeting": [
                "Здравейте! Аз съм AI асистентът на ГДПБЗН. Мога да ви помогна с информация за произшествия, екипи, ресурси и процедури. Как мога да ви бъда полезен?",
                "Здравейте! На ваше разположение съм. Мога да ви информирам за активните произшествия, да ви помогна със създаването на нов инцидент или да ви предоставя информация за ресурси и екипи.",
            ],
            "help": [
                "Мога да ви помогна със:\n"
                "• 📊 **Статистика** - брой активни произшествия, екипи на терен\n"
                "• 🚒 **Информация за екипи** - налични екипи и служители\n"
                "• 📦 **Ресурси** - налични ресурси и запаси\n"
                "• 🔥 **Създаване на произшествие** - регистриране на нов инцидент\n"
                "• ❓ **Отговори на въпроси** - процедури, статуси и други\n\n"
                "Просто ми задайте въпрос!",
                "На разположение съм! Мога да ви помогна с:\n"
                "- Информация за текущи произшествия\n"
                "- Данни за екипи и служители\n"
                "- Налични ресурси\n"
                "- Общи процедури и насоки",
            ],
            "incident_stats": [
                self._get_incident_stats(),
            ],
            "incident_create": [
                "За да създадете ново произшествие, отидете в секция **Произшествия** и натиснете бутона **+ Ново произшествие**. Попълнете типа, адреса, GPS координатите и изберете екипи. Или ми кажете детайлите и ще ви насоча.",
            ],
            "team_info": [
                self._get_team_info(),
            ],
            "resource_info": [
                self._get_resource_info(),
            ],
            "status_info": [
                self._get_status_info(),
            ],
            "weather": [
                "За съжаление нямам директен достъп до метеорологични данни. Препоръчвам да проверите в оперативния център за актуална информация за времето и посоката на вятъра.",
            ],
            "procedures": [
                "За конкретни процедури и правилници, моля обърнете се към оперативния център или проверете документацията на ГДПБЗН. Мога да ви помогна с основни насоки и информация за системата.",
            ],
            "emergency": [
                "🚨 **Спешен сигнал!** 🚨\n\nАко имате спешна ситуация, моля:\n1. Използвайте бутона за **SOS сигнал** на вашето устройство\n2. Свържете се с оперативния център\n3. Изпратете вашите GPS координати\n\nАко искате да регистрирате ново произшествие, отидете в секция Произшествия.",
            ],
            "farewell": [
                "На разположение съм! Ако имате нужда от помощ, просто ми пишете. Бъдете внимателни! 🚒",
                "Вилайте! При необходимост, пак съм тук. Безопасна работа! 🚒",
            ],
            "general": [
                self._get_general_response(message, incident_id),
            ],
        }

        selected = responses.get(context, responses["general"])
        return random.choice(selected) if isinstance(selected, list) else selected

    def _get_incident_stats(self):
        from app import db
        total = Incident.query.count()
        active = Incident.query.filter(Incident.status != "closed").count()
        closed = Incident.query.filter_by(status="closed").count()
        fires = Incident.query.join(IncidentType).filter(
            IncidentType.category == "fire"
        ).count()

        return (
            f"📊 **Статистика:**\n"
            f"• Общо произшествия: **{total}**\n"
            f"• Активни: **{active}**\n"
            f"• Приключени: **{closed}**\n"
            f"• Пожари: **{fires}**"
        )

    def _get_team_info(self):
        teams = Team.query.filter_by(is_active=True).all()
        if not teams:
            return "Няма налични екипи в момента."

        lines = ["🚒 **Налични екипи:**"]
        for t in teams:
            members = sum(1 for m in t.members if m.is_on_shift)
            truck = t.fire_truck.registration_number if t.fire_truck else "без автомобил"
            lines.append(f"• **{t.name}** - {members} човека, автомобил: {truck}")
        return "\n".join(lines)

    def _get_resource_info(self):
        resources = Resource.query.all()
        if not resources:
            return "Няма налични ресурси в системата."

        lines = ["📦 **Налични ресурси:**"]
        for r in resources:
            lines.append(f"• **{r.name}** - {r.quantity_available} {r.unit or ''} ({r.resource_type})")
        return "\n".join(lines)

    def _get_status_info(self):
        active = Incident.query.filter(
            Incident.status.in_(["registered", "dispatched", "en_route", "on_scene", "in_progress", "contained"])
        ).count()
        teams_out = sum(
            1 for t in Team.query.all()
            if any(m.is_on_shift for m in t.members)
        )
        return (
            f"🔄 **Актуално състояние:**\n"
            f"• Активни произшествия: **{active}**\n"
            f"• Екипи на смяна: **{teams_out}**\n"
            f"• Системата работи нормално ✅"
        )

    def _get_general_response(self, message, incident_id=None):
        keywords_fire = re.search(r'(пожар|fire|гор|пламък|дим|огън)', message)
        keywords_water = re.search(r'(вода|water|цистерн|хидрант|пяна)', message)
        keywords_help = re.search(r'(помощ|help|трябва|need|искам)', message)
        keywords_info = re.search(r'(информация|info|кажи|кой|какво|кога|къде)', message)

        if keywords_fire:
            return (
                "🔥 **Относно пожара:**\n\n"
                "При пожар е важно да:\n"
                "1. Определите типа и мащаба на пожара\n"
                "2. Осигурите водоснабдяване\n"
                "3. Определите посоката на вятъра\n"
                "4. Обезопасите района\n"
                "5. Координирате екипите\n\n"
                "Имате ли нужда от конкретна информация?"
            )
        elif keywords_water:
            return (
                "💧 **Водоснабдяване и ресурси:**\n\n"
                "За водоснабдяване при пожар:\n"
                "• Използвайте най-близкия хидрант\n"
                "• При нужда от цистерна - направете заявка през Ресурси\n"
                "• За горски пожари - осигурете водоизточници\n\n"
                "Мога да ви покажа наличните ресурси в системата."
            )
        elif keywords_help:
            return (
                "🤝 **Как мога да помогна?**\n\n"
                "Ето какво мога да направя за вас:\n"
                "• Покажа статистика за произшествия\n"
                "• Информация за екипи и ресурси\n"
                "• Помогна със създаване на нов инцидент\n"
                "• Отговоря на въпроси за процедури\n\n"
                "Какво ви интересува?"
            )
        elif keywords_info:
            return (
                "ℹ️ **Информация:**\n\n"
                "Мога да ви предоставя информация за:\n"
                "• **Произшествия** - брой, статус, детайли\n"
                "• **Екипи** - налични екипи и служители\n"
                "• **Ресурси** - налични запаси\n"
                "• **Статистика** - обобщени данни\n\n"
                "Какво точно ви интересува?"
            )
        else:
            tips = [
                "Можете да ме попитате за:\n• Броя на активните произшествия\n• Наличните екипи\n• Ресурсите в системата\n• Как да създадете нов инцидент",
                "Задайте ми въпрос! Например:\n• \"Колко са активните пожари?\"\n• \"Кои екипи са налични?\"\n• \"Какви ресурси имаме?\"",
                "На ваше разположение съм. Попитайте ме за статистика, екипи, ресурси или процедури.",
            ]
            if incident_id:
                inc = Incident.query.get(incident_id)
                if inc:
                    return (
                        f"📋 **Произшествие #{inc.incident_number}**\n"
                        f"• Тип: {inc.incident_type.name if inc.incident_type else 'N/A'}\n"
                        f"• Статус: {inc.status}\n"
                        f"• Адрес: {inc.address or 'N/A'}\n\n"
                        f"Имате ли нужда от допълнителна информация?"
                    )
            return random.choice(tips)


ai_chat_service = AIChatService()
