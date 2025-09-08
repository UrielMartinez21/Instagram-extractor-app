import json


def get_json_files_for_account(account_name, data_dir, logger):
        """ Search for all JSON files related to a specific account """
        if not account_name.strip():
            return []

        try:
            json_files = []
            # Search pattern: account_data_YYYYMMDDHHMM.json
            for file_path in data_dir.glob("*.json"):
                filename = file_path.name
                # Check if the file corresponds to the searched account
                if filename.startswith(f"{account_name}_data_"):
                    # Extract data from filename
                    timestamp_part = ""
                    try:
                        timestamp_part = filename.replace(f"{account_name}_data_", "").replace(".json", "")
                        # Format the timestamp part to a readable date
                        if len(timestamp_part) == 12:  # YYYYMMDDHHMM
                            year = timestamp_part[:4]
                            month = timestamp_part[4:6]
                            day = timestamp_part[6:8]
                            hour = timestamp_part[8:10]
                            minute = timestamp_part[10:12]
                            formatted_date = f"{day}/{month}/{year} {hour}:{minute}"
                            
                            json_files.append({
                                'filename': filename,
                                'path': str(file_path),
                                'display_name': f"{formatted_date} - {filename}",
                                'timestamp': timestamp_part
                            })
                    except Exception:
                        timestamp_part = ""
                        # If not able to parse the date, add the file anyway
                        json_files.append({
                            'filename': filename,
                            'path': str(file_path),
                            'display_name': filename,
                            'timestamp': ""
                        })

            # Order by timestamp (most recent first)
            json_files.sort(key=lambda x: x['timestamp'], reverse=True)
            return json_files

        except Exception as e:
            logger.error(f"Error buscando archivos para {account_name}: {e}")
            return []


def load_json_file(file_path: str) -> dict:
        """Load and validate a JSON file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Validate required keys
            required_keys = ['account', 'followers', 'following', 'extraction_date']
            for key in required_keys:
                if key not in data:
                    raise ValueError(f"El archivo no tiene la estructura esperada. Falta la clave: {key}")

            return data

        except json.JSONDecodeError:
            raise ValueError("El archivo no es un JSON válido")
        except Exception as e:
            raise ValueError(f"Error cargando el archivo: {str(e)}")


def format_json_data(data: dict) -> str:
        account_info = data.get('account_info', {})
        stats = data.get('stats', {})

        # Create the formatted text
        formatted_text = f"""
            📊 INFORMACIÓN DE LA CUENTA
            ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

            👤 Cuenta: @{data.get('account', 'N/A')}
            📝 Nombre: {account_info.get('full_name', 'N/A')}
            🔒 Privada: {'Sí' if account_info.get('is_private', False) else 'No'}
            📅 Extracción: {data.get('extraction_date', 'N/A')}

            📈 ESTADÍSTICAS
            ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

            👥 Seguidores: {stats.get('total_followers', 0)} / {stats.get('expected_followers', 0)} esperados
            ➡️ Siguiendo: {stats.get('total_following', 0)} / {stats.get('expected_following', 0)} esperados

            📋 LISTAS EXTRAÍDAS
            ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

            📂 Seguidores ({len(data.get('followers', []))})
            📂 Siguiendo ({len(data.get('following', []))})
        """

        return formatted_text


def format_comparison_data(comparison: dict) -> str:
        """Formatea los datos de comparación para mostrar"""
        info = comparison['comparison_info']
        stats = comparison['stats']
        
        formatted_text = f"""
            📊 COMPARACIÓN DE DATOS - @{comparison['account']}
            ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

            📁 ARCHIVOS COMPARADOS
            ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
            
            📅 Archivo 1: {info['file1']['filename']}
            📅 Fecha: {info['file1']['date']}
            👥 Seguidores: {info['file1']['followers_count']}
            ➡️ Siguiendo: {info['file1']['following_count']}
            
            📅 Archivo 2: {info['file2']['filename']}
            📅 Fecha: {info['file2']['date']}
            👥 Seguidores: {info['file2']['followers_count']}
            ➡️ Siguiendo: {info['file2']['following_count']}

            📈 CAMBIOS DETECTADOS
            ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

            👥 SEGUIDORES:
            • Ganados: {stats['followers_gained']}
            • Perdidos: {stats['followers_lost']}
            • Cambio neto: {stats['net_followers_change']:+d}

            ➡️ SIGUIENDO:
            • Nuevos seguidos: {stats['new_following_count']}
            • Dejó de seguir: {stats['unfollowed_count']}
            • Cambio neto: {stats['net_following_change']:+d}

            🔄 RELACIONES ACTUALES
            ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

            💫 Se siguen mutuamente: {stats['mutual_follows_count']}
            ➡️ Sigue pero no lo siguen: {stats['follows_but_not_followed_count']}
            ⬅️ Lo siguen pero no sigue: {stats['followed_but_not_following_count']}
        """

        return formatted_text