import json
from datetime import datetime
from pathlib import Path

class AccessLogger:
    def __init__(self):
        self.log_file = "logs/access_log.json"
        self._init_log_file()
    
    def _init_log_file(self):
        """Inicializa o arquivo de log se não existir"""
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        if not Path(self.log_file).exists():
            self._save_logs([])
    
    def _load_logs(self):
        """Carrega os logs existentes"""
        try:
            with open(self.log_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return []
    
    def _save_logs(self, logs):
        """Salva os logs no arquivo"""
        with open(self.log_file, 'w', encoding='utf-8') as f:
            json.dump(logs, f, ensure_ascii=False, indent=4)
    
    def log_access(self, ip, page):
        """Registra um novo acesso"""
        logs = self._load_logs()
        
        new_log = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "ip": ip,
            "page": page
        }
        
        logs.append(new_log)
        self._save_logs(logs)
    
    def get_access_stats(self):
        """Retorna estatísticas básicas de acesso"""
        logs = self._load_logs()
        
        stats = {
            "total_acessos": len(logs),
            "acessos_hoje": 0,
            "paginas_mais_acessadas": {},
            "ips_unicos": len(set(log["ip"] for log in logs)),
            "ultimo_acesso": None
        }
        
        hoje = datetime.now().date()
        
        for log in logs:
            # Conta acessos de hoje
            log_date = datetime.strptime(log["timestamp"], "%Y-%m-%d %H:%M:%S").date()
            if log_date == hoje:
                stats["acessos_hoje"] += 1
            
            # Conta acessos por página
            page = log["page"]
            if page in stats["paginas_mais_acessadas"]:
                stats["paginas_mais_acessadas"][page] += 1
            else:
                stats["paginas_mais_acessadas"][page] = 1
        
        # Pega informações do último acesso
        if logs:
            ultimo_log = logs[-1]
            stats["ultimo_acesso"] = {
                "horario": ultimo_log["timestamp"],
                "ip": ultimo_log["ip"]
            }
        
        return stats 