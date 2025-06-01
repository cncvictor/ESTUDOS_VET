import json
import os
from datetime import datetime
from pathlib import Path

class UserManager:
    def __init__(self):
        self.data_dir = Path("user_data")
        self.data_dir.mkdir(exist_ok=True)
        self.stats_file = self.data_dir / "stats.json"
        self.notes_file = self.data_dir / "notes.json"
        self.favorites_file = self.data_dir / "favorites.json"
        self._init_files()
        
    def _init_files(self):
        """Inicializa os arquivos de dados se não existirem."""
        if not self.stats_file.exists():
            initial_stats = {
                "total_study_time": 0,
                "items_studied": 0,
                "correct_answers": 0,
                "total_answers": 0,
                "last_session": None,
                "notes_count": 0,
                "favorites_count": 0
            }
            self._save_stats(initial_stats)
            
        if not self.notes_file.exists():
            self._save_notes({})
            
        if not self.favorites_file.exists():
            self._save_favorites([])
    
    def _load_stats(self):
        """Carrega as estatísticas do usuário."""
        with open(self.stats_file, 'r') as f:
            return json.load(f)
    
    def _save_stats(self, stats):
        """Salva as estatísticas do usuário."""
        with open(self.stats_file, 'w') as f:
            json.dump(stats, f, indent=4)
    
    def _load_notes(self):
        """Carrega as notas do usuário."""
        with open(self.notes_file, 'r') as f:
            return json.load(f)
    
    def _save_notes(self, notes):
        """Salva as notas do usuário."""
        with open(self.notes_file, 'w') as f:
            json.dump(notes, f, indent=4)
    
    def _load_favorites(self):
        """Carrega os favoritos do usuário."""
        with open(self.favorites_file, 'r') as f:
            return json.load(f)
    
    def _save_favorites(self, favorites):
        """Salva os favoritos do usuário."""
        with open(self.favorites_file, 'w') as f:
            json.dump(favorites, f, indent=4)
    
    def track_progress(self, item_id, correct=True):
        """Registra o progresso do usuário."""
        stats = self._load_stats()
        stats["items_studied"] += 1
        if correct:
            stats["correct_answers"] += 1
        stats["total_answers"] += 1
        stats["last_session"] = datetime.now().isoformat()
        self._save_stats(stats)
    
    def add_note(self, item_id, note):
        """Adiciona uma nota a um item."""
        notes = self._load_notes()
        if item_id not in notes:
            notes[item_id] = []
        notes[item_id].append({
            "text": note,
            "timestamp": datetime.now().isoformat()
        })
        self._save_notes(notes)
    
    def toggle_favorite(self, item_id):
        """Alterna o status de favorito de um item."""
        favorites = self._load_favorites()
        if item_id in favorites:
            favorites.remove(item_id)
        else:
            favorites.append(item_id)
        self._save_favorites(favorites)
    
    def get_statistics(self):
        """Retorna as estatísticas do usuário."""
        try:
            stats = self._load_stats()
            notes = self._load_notes()
            favorites = self._load_favorites()
            
            return {
                "total_study_time": stats.get("total_study_time", 0),
                "items_studied": stats.get("items_studied", 0),
                "correct_answers": stats.get("correct_answers", 0),
                "total_answers": stats.get("total_answers", 1),
                "notes_count": sum(len(notes_list) for notes_list in notes.values()),
                "favorites_count": len(favorites)
            }
        except Exception as e:
            print(f"Erro ao carregar estatísticas: {e}")
            return {
                "total_study_time": 0,
                "items_studied": 0,
                "correct_answers": 0,
                "total_answers": 0,
                "notes_count": 0,
                "favorites_count": 0
            } 