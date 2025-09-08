import json
from pathlib import Path

class InstagramComparator:
    def __init__(self, data_dir, logger):
        self.data_dir = data_dir
        self.logger = logger

    def load_data(self, filename):
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
            self.logger.info(f"Cargado: {filename}")
            return data
        except Exception as e:
            self.logger.error(f"Error cargando {filename}: {e}")
            return None

    def find_account_files(self, account_name):
        pattern = f"{account_name}_data_*.json"
        files = []
        for file_path in self.data_dir.glob(pattern):
            files.append(str(file_path))
        files.sort()
        return files

    def compare_data(self, file1, file2):
        # Cargar datos
        data1 = self.load_data(file1)
        data2 = self.load_data(file2)
        
        if not data1 or not data2:
            return None
        
        # Verificar que sean de la misma cuenta
        if data1['account'] != data2['account']:
            self.logger.error("Los archivos son de cuentas diferentes")
            return None
        
        account_name = data1['account']
        
        # Convertir listas a sets para operaciones de conjuntos
        followers1 = set(data1['followers'])
        following1 = set(data1['following'])
        
        followers2 = set(data2['followers'])
        following2 = set(data2['following'])
        
        # Análisis de cambios en seguidores
        new_followers = followers2 - followers1  # Nuevos seguidores
        lost_followers = followers1 - followers2  # Seguidores perdidos
        
        # Análisis de cambios en seguidos
        new_following = following2 - following1  # Nuevos seguidos
        unfollowed = following1 - following2     # Dejó de seguir
        
        # Análisis de relaciones actuales (del archivo más reciente)
        mutual_follows = followers2 & following2  # Se siguen mutuamente
        follows_but_not_followed = following2 - followers2  # Sigue pero no lo siguen
        followed_but_not_following = followers2 - following2  # Lo siguen pero no sigue
        
        # Crear reporte completo
        comparison = {
            "account": account_name,
            "comparison_info": {
                "file1": {
                    "filename": Path(file1).name,
                    "date": data1.get('extraction_date', 'No disponible'),
                    "followers_count": len(followers1),
                    "following_count": len(following1)
                },
                "file2": {
                    "filename": Path(file2).name,
                    "date": data2.get('extraction_date', 'No disponible'),
                    "followers_count": len(followers2),
                    "following_count": len(following2)
                }
            },
            "changes": {
                "new_followers": sorted(list(new_followers)),
                "lost_followers": sorted(list(lost_followers)),
                "new_following": sorted(list(new_following)),
                "unfollowed": sorted(list(unfollowed))
            },
            "current_relationships": {
                "mutual_follows": sorted(list(mutual_follows)),
                "follows_but_not_followed": sorted(list(follows_but_not_followed)),
                "followed_but_not_following": sorted(list(followed_but_not_following))
            },
            "stats": {
                "followers_gained": len(new_followers),
                "followers_lost": len(lost_followers),
                "net_followers_change": len(new_followers) - len(lost_followers),
                "new_following_count": len(new_following),
                "unfollowed_count": len(unfollowed),
                "net_following_change": len(new_following) - len(unfollowed),
                "mutual_follows_count": len(mutual_follows),
                "follows_but_not_followed_count": len(follows_but_not_followed),
                "followed_but_not_following_count": len(followed_but_not_following)
            }
        }
        
        return comparison