import os
import time
import json
from datetime import datetime
from instagrapi import Client

class SimpleInstagramExtractor:
    def __init__(self, sessions_dir, data_dir, logger):
        self.client = Client()
        self.logged_in = False
        self.session_file = sessions_dir / "session.json"
        self.data_dir = data_dir
        self.logger = logger

    def login(self, username, password) -> bool:
        try:
            # Try to load existing session
            if os.path.exists(self.session_file):
                try:
                    self.logger.info("Intentando cargar sesión existente...")
                    self.client.load_settings(self.session_file)
                    self.logger.info("Sesión cargada desde archivo")
                    self.logged_in = True
                    return True
                except Exception as e:
                    self.logger.warning(f"No se pudo cargar la sesión: {e}")
                    # If loading fails, remove the corrupted session file
                    try:
                        os.remove(self.session_file)
                    except Exception:
                        pass

            # Loggin again
            self.logger.info(f"Iniciando sesión para usuario: {username}")
            self.client.login(username, password)

            # Save session
            self.client.dump_settings(self.session_file)
            self.logger.info("Sesión iniciada y guardada")
            self.logged_in = True
            return True

        except Exception as e:
            self.logger.error(f"Error de login: {e}")
            return False

    def verify_account_access(self, username) -> dict:
        try:
            self.logger.info(f"Verificando acceso para @{username}...")
            user_info = self.client.user_info_by_username(username)

            access_info = {
                'can_access': True,
                'is_private': user_info.is_private,
                'follower_count': user_info.follower_count,
                'following_count': user_info.following_count,
                'full_name': user_info.full_name or username
            }

            if user_info.is_private:
                self.logger.warning(f"@{username} es una cuenta privada")
            else:
                self.logger.info(f"@{username} es una cuenta pública")

            self.logger.info(f"La cuenta tiene {user_info.follower_count} seguidores y sigue a {user_info.following_count}")
            return access_info

        except Exception as e:
            self.logger.error(f"No se puede acceder a @{username}: {e}")
            return {'can_access': False, 'error': str(e)}

    def get_followers_list(self, username) -> list:
        try:
            user_info = self.client.user_info_by_username(username)
            user_id = user_info.pk

            self.logger.info(f"Obteniendo seguidores de @{username} - Total esperado: {user_info.follower_count}")

            # Get all followers
            followers_dict = self.client.user_followers(user_id)

            # Extract only usernames
            followers_list = []
            for follower_info in followers_dict.values():
                followers_list.append(follower_info.username)

            self.logger.info(f"{len(followers_list)} seguidores obtenidos")
            return followers_list

        except Exception as e:
            self.logger.error(f"Error obteniendo seguidores de @{username}: {e}")
            return []

    def get_following_list(self, username) -> list:
        try:
            user_info = self.client.user_info_by_username(username)
            user_id = user_info.pk

            self.logger.info(f"Obteniendo seguidos de @{username} - Total esperado: {user_info.following_count}")

            # Get all following
            following_dict = self.client.user_following(user_id)

            # Extract only usernames
            following_list = []
            for following_info in following_dict.values():
                following_list.append(following_info.username)

            self.logger.info(f"{len(following_list)} seguidos obtenidos")
            return following_list

        except Exception as e:
            self.logger.error(f"Error obteniendo seguidos de @{username}: {e}")
            return []

    def extract_account(self, target_username) -> dict:
        if not self.logged_in:
            self.logger.error("Debes iniciar sesión primero")
            return None

        self.logger.info(f"Iniciando extracción de datos de @{target_username}")

        # Check account access
        access_info = self.verify_account_access(target_username)
        if not access_info['can_access']:
            self.logger.error(f"No se puede acceder a la cuenta @{target_username}")
            return None

        # Get followers
        self.logger.info("=" * 50)
        self.logger.info("PASO 1: EXTRAYENDO SEGUIDORES")
        self.logger.info("=" * 50)
        followers = self.get_followers_list(target_username)

        # Delay to avoid rate limits
        self.logger.info("⏳ Pausa de 5 segundos entre requests...")
        time.sleep(5)

        # Get following
        self.logger.info("=" * 50)
        self.logger.info("PASO 2: EXTRAYENDO SEGUIDOS")
        self.logger.info("=" * 50)
        following = self.get_following_list(target_username)

        # Create data structure
        timestamp = datetime.now()
        account_data = {
            "account": target_username,
            "followers": followers,
            "following": following,
            "extraction_date": timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            "account_info": access_info,
            "stats": {
                "total_followers": len(followers),
                "total_following": len(following),
                "expected_followers": access_info.get('follower_count', 0),
                "expected_following": access_info.get('following_count', 0)
            }
        }

        # Generate filename
        timestamp_str = timestamp.strftime('%Y%m%d%H%M')
        filename = f"{target_username}_data_{timestamp_str}.json"
        filepath = self.data_dir / filename

        # Guardar archivo JSON
        self.logger.info("=" * 50)
        self.logger.info("PASO 3: GUARDANDO ARCHIVO")
        self.logger.info("=" * 50)

        try:
            self.logger.info(f"Guardando datos en: {filepath}")

            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(account_data, f, indent=2, ensure_ascii=False)

            # Check file creation
            if filepath.exists():
                file_size = filepath.stat().st_size
                self.logger.info("Archivo creado exitosamente!")
                self.logger.info(f"Ubicación: {filepath.absolute()}")
                self.logger.info(f"Tamaño: {file_size} bytes")
            else:
                self.logger.error("El archivo no se pudo crear")
                return None

        except Exception as e:
            self.logger.error(f"Error guardando archivo: {e}")
            return None

        # Mostrar resumen final
        self.logger.info("=" * 50)
        self.logger.info("EXTRACCIÓN COMPLETADA")
        self.logger.info("=" * 50)
        self.logger.info(f"Cuenta: @{target_username}")
        self.logger.info(f"Seguidores extraídos: {len(followers)} / {access_info.get('follower_count', 'N/A')} esperados")
        self.logger.info(f"Seguidos extraídos: {len(following)} / {access_info.get('following_count', 'N/A')} esperados")
        self.logger.info(f"Archivo: {filename}")
        self.logger.info(f"Fecha: {account_data['extraction_date']}")

        return {
            'success': True,
            'data': account_data,
            'filepath': str(filepath),
            'filename': filename
        }