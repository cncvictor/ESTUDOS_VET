import json
from datetime import datetime, timedelta
from pathlib import Path

class SpacedRevision:
    def __init__(self):
        self.data_dir = Path("user_data")
        self.data_dir.mkdir(exist_ok=True)
        self.revision_file = self.data_dir / "revisions.json"
        self._init_file()
    
    def _init_file(self):
        """Inicializa o arquivo de revisões se não existir."""
        if not self.revision_file.exists():
            self._save_revisions({
                "items": {},
                "schedule": {}
            })
    
    def _load_revisions(self):
        """Carrega as revisões do arquivo."""
        with open(self.revision_file, 'r') as f:
            return json.load(f)
    
    def _save_revisions(self, data):
        """Salva as revisões no arquivo."""
        with open(self.revision_file, 'w') as f:
            json.dump(data, f, indent=4, default=str)
    
    def add_item(self, item_id, title, category, difficulty=0.5):
        """Adiciona um novo item para revisão."""
        data = self._load_revisions()
        
        if item_id not in data["items"]:
            data["items"][item_id] = {
                "title": title,
                "category": category,
                "difficulty": difficulty,
                "reviews": 0,
                "last_review": None,
                "next_review": datetime.now().isoformat()
            }
            
            data["schedule"][datetime.now().date().isoformat()] = data["schedule"].get(
                datetime.now().date().isoformat(), []
            ) + [item_id]
            
            self._save_revisions(data)
    
    def review_item(self, item_id, score):
        """Registra uma revisão e agenda a próxima."""
        data = self._load_revisions()
        
        if item_id in data["items"]:
            item = data["items"][item_id]
            item["reviews"] += 1
            item["last_review"] = datetime.now().isoformat()
            
            # Ajusta a dificuldade baseado no score (0-1)
            item["difficulty"] = max(0.1, min(1.0, item["difficulty"] + (0.5 - score)))
            
            # Calcula próxima revisão
            days_to_next = int(2 ** (item["reviews"] * item["difficulty"]))
            next_date = (datetime.now() + timedelta(days=days_to_next)).date()
            
            item["next_review"] = next_date.isoformat()
            
            # Agenda próxima revisão
            data["schedule"][next_date.isoformat()] = data["schedule"].get(
                next_date.isoformat(), []
            ) + [item_id]
            
            self._save_revisions(data)
    
    def get_due_items(self, days_ahead=7):
        """Retorna itens para revisão nos próximos dias."""
        data = self._load_revisions()
        due_items = []
        
        start_date = datetime.now().date()
        end_date = start_date + timedelta(days=days_ahead)
        
        current = start_date
        while current <= end_date:
            if current.isoformat() in data["schedule"]:
                for item_id in data["schedule"][current.isoformat()]:
                    if item_id in data["items"]:
                        item = data["items"][item_id]
                        due_items.append({
                            "id": item_id,
                            "title": item["title"],
                            "category": item["category"],
                            "due_date": current.isoformat(),
                            "reviews": item["reviews"]
                        })
            current += timedelta(days=1)
        
        return due_items
    
    def get_statistics(self):
        """Retorna estatísticas das revisões."""
        data = self._load_revisions()
        
        total_items = len(data["items"])
        total_reviews = sum(item["reviews"] for item in data["items"].values())
        avg_difficulty = sum(item["difficulty"] for item in data["items"].values()) / max(1, total_items)
        
        categories = {}
        for item in data["items"].values():
            cat = item["category"]
            if cat not in categories:
                categories[cat] = 0
            categories[cat] += 1
        
        return {
            "total_items": total_items,
            "total_reviews": total_reviews,
            "average_difficulty": avg_difficulty,
            "categories": categories
        } 