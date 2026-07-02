from app.models.chat import ChatTemplate, ChatMessage
from app.models.incident import Incident
import random


class AIService:
    @staticmethod
    def get_keywords(text):
        text = text.lower()
        keywords = []
        word_map = {
            "fire": "fire", "пожар": "fire", "гор": "fire", "плам": "fire",
            "water": "water", "вода": "water", "цистерн": "water", "хидрант": "water",
            "help": "help", "помощ": "help", "нужда": "help", "mayday": "help",
            "backup": "backup", "подкреп": "backup", "усилв": "backup",
            "arrive": "arrival", "пристиг": "arrival", "на място": "arrival", "там": "arrival",
            "status": "status", "статус": "status", "ситуац": "status", "положен": "status",
            "fuel": "fuel", "горив": "fuel", "бензин": "fuel", "дизел": "fuel",
            "injured": "medical", "ранен": "medical", "пострадал": "medical", "медиц": "medical",
            "contain": "contain", "овлад": "contain", "спря": "contain", "локализ": "contain",
            "evacuate": "evacuate", "евaky": "evacuate", "извед": "evacuate",
        }
        for word, category in word_map.items():
            if word in text:
                keywords.append(category)
        return keywords

    @staticmethod
    def suggest_response(incident_id, last_message=None):
        templates = ChatTemplate.query.filter_by(is_active=True).all()
        keywords = []

        if last_message:
            keywords = AIService.get_keywords(last_message)

        if incident_id:
            incident = Incident.query.get(incident_id)
            if incident:
                status_map = {
                    "registered": ["arrival", "status"],
                    "dispatched": ["arrival", "status"],
                    "en_route": ["arrival", "status"],
                    "on_scene": ["status", "fire", "water", "help"],
                    "in_progress": ["status", "water", "backup", "fuel"],
                    "contained": ["status", "contain"],
                    "closed": ["status"],
                }
                keywords.extend(status_map.get(incident.status, []))

        scored = []
        for t in templates:
            score = 0
            t_lower = t.message_text.lower()
            for kw in set(keywords):
                kw_map = {
                    "fire": ["fire", "пожар", "гор", "плам"],
                    "water": ["water", "вода", "цистерн", "хидрант"],
                    "help": ["help", "помощ", "нужда", "mayday"],
                    "backup": ["backup", "подкреп", "усилв"],
                    "arrival": ["arrive", "пристиг", "на място"],
                    "status": ["status", "статус", "ситуац"],
                    "fuel": ["fuel", "горив"],
                    "medical": ["injured", "ранен", "пострадал", "медиц"],
                    "contain": ["contain", "овлад", "локализ"],
                    "evacuate": ["evacuate", "извед"],
                }
                for word in kw_map.get(kw, []):
                    if word in t_lower:
                        score += 2
                if t.category == kw:
                    score += 3
            scored.append((score, t))

        scored.sort(key=lambda x: -x[0])
        top = [t for score, t in scored if score > 0][:3]

        if not top and templates:
            top = random.sample(templates, min(2, len(templates)))

        return [
            {
                "id": t.id,
                "category": t.category,
                "message_text": t.message_text,
                "relevance": "high" if i == 0 else "medium",
            }
            for i, t in enumerate(top)
        ]

    @staticmethod
    def auto_reply(incident_id, channel_id, user_message):
        keywords = AIService.get_keywords(user_message)
        templates = ChatTemplate.query.filter_by(is_active=True).all()

        reply_map = {
            "help": "Copy that. Assistance is on the way. What is your exact location?",
            "mayday": "MAYDAY received! Coordinating rescue team to your position immediately!",
            "fire": "Roger. Assessing situation. Keep us updated on fire behavior.",
            "water": "Request received. Dispatching additional water tanker to your location.",
            "arrival": "Copy. Team arrived on scene. Report initial assessment when ready.",
            "backup": "Backup units are being dispatched. ETA 10 minutes.",
            "status": "Copy. Thanks for the update. Keep us informed of any changes.",
            "contain": "Excellent work. Continue cooling operations and monitor for hotspots.",
            "medical": "Medical team is being dispatched to your coordinates. Stay with the victim.",
            "fuel": "Fuel resupply is on its way. ETA 15 minutes.",
            "evacuate": "Evacuation protocol initiated. Proceed to designated assembly point.",
        }

        for kw, reply in reply_map.items():
            if kw in keywords:
                return reply

        return None
