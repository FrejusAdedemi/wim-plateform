# apps/youtube/services.py
"""
Service YouTube pour intégrer l'API YouTube Data v3
Gestion des playlists, vidéos et métadonnées
"""

import os
import re
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import isodate
import requests
from django.core.cache import cache
from django.conf import settings
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)


class YouTubeAPIError(Exception):
    """Exception personnalisée pour les erreurs YouTube API"""
    pass


class YouTubeService:
    """Service principal pour interagir avec l'API YouTube"""

    def __init__(self):
        self.api_key = getattr(settings, 'YOUTUBE_API_KEY', '')
        self.base_url = 'https://www.googleapis.com/youtube/v3'
        self.timeout = getattr(settings, 'YOUTUBE_API_TIMEOUT', 30)
        self.cache_duration = getattr(settings, 'YOUTUBE_CACHE_DURATION', 3600)

        if not self.api_key:
            raise YouTubeAPIError("YouTube API key not configured")

    def _make_request(self, endpoint: str, params: dict) -> dict:
        """Effectue une requête vers l'API YouTube avec gestion d'erreur"""
        params['key'] = self.api_key

        # Créer une clé de cache unique
        cache_key = f"youtube_{endpoint}_{hash(str(sorted(params.items())))}"

        # Vérifier le cache
        cached_result = cache.get(cache_key)
        if cached_result:
            logger.debug(f"Cache hit for {endpoint}")
            return cached_result

        try:
            url = f"{self.base_url}/{endpoint}"
            response = requests.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()

            result = response.json()

            # Mettre en cache le résultat
            cache.set(cache_key, result, self.cache_duration)

            return result

        except requests.exceptions.RequestException as e:
            logger.error(f"YouTube API request failed: {e}")
            raise YouTubeAPIError(f"API request failed: {e}")
        except Exception as e:
            logger.error(f"Unexpected error in YouTube API: {e}")
            raise YouTubeAPIError(f"Unexpected error: {e}")

    def extract_video_id(self, url: str) -> Optional[str]:
        """Extrait l'ID d'une vidéo YouTube à partir de son URL"""
        patterns = [
            r'(?:v=|\/)([0-9A-Za-z_-]{11}).*',
            r'(?:embed\/)([0-9A-Za-z_-]{11})',
            r'(?:youtu\.be\/)([0-9A-Za-z_-]{11})'
        ]

        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)

        # Si c'est déjà un ID de 11 caractères
        if len(url) == 11 and re.match(r'^[0-9A-Za-z_-]+$', url):
            return url

        return None

    def extract_playlist_id(self, url: str) -> Optional[str]:
        """Extrait l'ID d'une playlist YouTube à partir de son URL"""
        patterns = [
            r'list=([0-9A-Za-z_-]+)',
            r'playlist\?list=([0-9A-Za-z_-]+)'
        ]

        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)

        return None

    def extract_channel_id(self, url: str) -> Optional[str]:
        """Extrait l'ID d'une chaîne YouTube à partir de son URL"""
        patterns = [
            r'channel\/([0-9A-Za-z_-]+)',
            r'c\/([0-9A-Za-z_-]+)',
            r'user\/([0-9A-Za-z_-]+)',
            r'@([0-9A-Za-z_-]+)'
        ]

        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)

        return None

    def get_video_details(self, video_id: str) -> Optional[Dict]:
        """Récupère les détails d'une vidéo YouTube"""
        try:
            params = {
                'part': 'snippet,contentDetails,statistics',
                'id': video_id
            }

            response = self._make_request('videos', params)

            if not response.get('items'):
                logger.warning(f"Video not found: {video_id}")
                return None

            video = response['items'][0]
            snippet = video['snippet']
            content_details = video['contentDetails']
            statistics = video['statistics']

            # Convertir la durée ISO 8601 en secondes
            duration_iso = content_details.get('duration', 'PT0S')
            duration_seconds = int(isodate.parse_duration(duration_iso).total_seconds())

            # Parser la date de publication
            published_at = datetime.fromisoformat(
                snippet['publishedAt'].replace('Z', '+00:00')
            )

            return {
                'id': video_id,
                'title': snippet['title'],
                'description': snippet['description'],
                'channel_id': snippet['channelId'],
                'channel_name': snippet['channelTitle'],
                'published_at': published_at,
                'duration_seconds': duration_seconds,
                'view_count': int(statistics.get('viewCount', 0)),
                'like_count': int(statistics.get('likeCount', 0)),
                'thumbnail_url': self._get_best_thumbnail(snippet['thumbnails']),
                'tags': snippet.get('tags', []),
                'category_id': snippet.get('categoryId'),
                'language': snippet.get('defaultLanguage', 'en'),
            }

        except Exception as e:
            logger.error(f"Error getting video details for {video_id}: {e}")
            return None

    def get_videos_details(self, video_ids: List[str]) -> List[Dict]:
        """Récupère les détails de plusieurs vidéos en une seule requête"""
        if not video_ids:
            return []

        try:
            # L'API permet jusqu'à 50 IDs par requête
            chunk_size = 50
            all_videos = []

            for i in range(0, len(video_ids), chunk_size):
                chunk = video_ids[i:i + chunk_size]
                ids_string = ','.join(chunk)

                params = {
                    'part': 'snippet,contentDetails,statistics',
                    'id': ids_string
                }

                response = self._make_request('videos', params)

                for video in response.get('items', []):
                    try:
                        snippet = video['snippet']
                        content_details = video['contentDetails']
                        statistics = video['statistics']

                        duration_iso = content_details.get('duration', 'PT0S')
                        duration_seconds = int(isodate.parse_duration(duration_iso).total_seconds())

                        published_at = datetime.fromisoformat(
                            snippet['publishedAt'].replace('Z', '+00:00')
                        )

                        video_data = {
                            'id': video['id'],
                            'title': snippet['title'],
                            'description': snippet['description'],
                            'channel_id': snippet['channelId'],
                            'channel_name': snippet['channelTitle'],
                            'published_at': published_at,
                            'duration_seconds': duration_seconds,
                            'view_count': int(statistics.get('viewCount', 0)),
                            'like_count': int(statistics.get('likeCount', 0)),
                            'thumbnail_url': self._get_best_thumbnail(snippet['thumbnails']),
                            'tags': snippet.get('tags', []),
                        }

                        all_videos.append(video_data)

                    except Exception as e:
                        logger.error(f"Error parsing video {video.get('id')}: {e}")
                        continue

            return all_videos

        except Exception as e:
            logger.error(f"Error getting videos details: {e}")
            return []

    def get_playlist_details(self, playlist_id: str) -> Optional[Dict]:
        """Récupère les détails d'une playlist"""
        try:
            params = {
                'part': 'snippet,contentDetails',
                'id': playlist_id
            }

            response = self._make_request('playlists', params)

            if not response.get('items'):
                logger.warning(f"Playlist not found: {playlist_id}")
                return None

            playlist = response['items'][0]
            snippet = playlist['snippet']
            content_details = playlist['contentDetails']

            return {
                'id': playlist_id,
                'title': snippet['title'],
                'description': snippet['description'],
                'channel_id': snippet['channelId'],
                'channel_name': snippet['channelTitle'],
                'published_at': datetime.fromisoformat(
                    snippet['publishedAt'].replace('Z', '+00:00')
                ),
                'thumbnail_url': self._get_best_thumbnail(snippet['thumbnails']),
                'video_count': content_details['itemCount'],
            }

        except Exception as e:
            logger.error(f"Error getting playlist details for {playlist_id}: {e}")
            return None

    def get_playlist_videos(self, playlist_id: str, max_results: int = 50) -> List[Dict]:
        """Récupère les vidéos d'une playlist"""
        try:
            all_videos = []
            next_page_token = None

            while len(all_videos) < max_results:
                params = {
                    'part': 'snippet,contentDetails',
                    'playlistId': playlist_id,
                    'maxResults': min(50, max_results - len(all_videos))
                }

                if next_page_token:
                    params['pageToken'] = next_page_token

                response = self._make_request('playlistItems', params)

                if not response.get('items'):
                    break

                # Extraire les IDs des vidéos
                video_ids = []
                for item in response['items']:
                    video_id = item['snippet']['resourceId']['videoId']
                    video_ids.append(video_id)

                # Récupérer les détails des vidéos
                videos_details = self.get_videos_details(video_ids)
                all_videos.extend(videos_details)

                next_page_token = response.get('nextPageToken')
                if not next_page_token:
                    break

            return all_videos[:max_results]

        except Exception as e:
            logger.error(f"Error getting playlist videos for {playlist_id}: {e}")
            return []

    def get_channel_videos(self, channel_id: str, max_results: int = 50) -> List[Dict]:
        """Récupère les vidéos d'une chaîne"""
        try:
            # D'abord, obtenir la playlist des uploads de la chaîne
            params = {
                'part': 'contentDetails',
                'id': channel_id
            }

            response = self._make_request('channels', params)

            if not response.get('items'):
                logger.warning(f"Channel not found: {channel_id}")
                return []

            uploads_playlist_id = (
                response['items'][0]
                ['contentDetails']
                ['relatedPlaylists']
                ['uploads']
            )

            # Récupérer les vidéos de la playlist uploads
            return self.get_playlist_videos(uploads_playlist_id, max_results)

        except Exception as e:
            logger.error(f"Error getting channel videos for {channel_id}: {e}")
            return []

    def search_videos(self, query: str, max_results: int = 10) -> List[Dict]:
        """Recherche de vidéos par mot-clé"""
        try:
            params = {
                'part': 'snippet',
                'q': query,
                'type': 'video',
                'maxResults': min(max_results, 50),
                'order': 'relevance'
            }

            response = self._make_request('search', params)

            if not response.get('items'):
                return []

            # Extraire les IDs des vidéos
            video_ids = [item['id']['videoId'] for item in response['items']]

            # Récupérer les détails complets
            return self.get_videos_details(video_ids)

        except Exception as e:
            logger.error(f"Error searching videos for '{query}': {e}")
            return []

    def get_channel_info(self, channel_id: str) -> Optional[Dict]:
        """Récupère les informations d'une chaîne"""
        try:
            params = {
                'part': 'snippet,statistics',
                'id': channel_id
            }

            response = self._make_request('channels', params)

            if not response.get('items'):
                logger.warning(f"Channel not found: {channel_id}")
                return None

            channel = response['items'][0]
            snippet = channel['snippet']
            statistics = channel['statistics']

            return {
                'id': channel_id,
                'title': snippet['title'],
                'description': snippet['description'],
                'published_at': datetime.fromisoformat(
                    snippet['publishedAt'].replace('Z', '+00:00')
                ),
                'thumbnail_url': self._get_best_thumbnail(snippet['thumbnails']),
                'subscriber_count': int(statistics.get('subscriberCount', 0)),
                'video_count': int(statistics.get('videoCount', 0)),
                'view_count': int(statistics.get('viewCount', 0)),
            }

        except Exception as e:
            logger.error(f"Error getting channel info for {channel_id}: {e}")
            return None

    def _get_best_thumbnail(self, thumbnails: dict) -> str:
        """Sélectionne la meilleure qualité de miniature disponible"""
        # Ordre de préférence des qualités
        qualities = ['maxres', 'high', 'medium', 'standard', 'default']

        for quality in qualities:
            if quality in thumbnails:
                return thumbnails[quality]['url']

        return ''

    def validate_video_accessibility(self, video_id: str) -> bool:
        """Vérifie si une vidéo est accessible (publique, non supprimée)"""
        try:
            video_data = self.get_video_details(video_id)
            return video_data is not None
        except Exception as e:
            logger.error(f"Error validating video {video_id}: {e}")
            return False

    def get_video_captions(self, video_id: str) -> List[Dict]:
        """Récupère la liste des sous-titres disponibles pour une vidéo"""
        try:
            params = {
                'part': 'snippet',
                'videoId': video_id
            }

            response = self._make_request('captions', params)

            captions = []
            for item in response.get('items', []):
                snippet = item['snippet']
                captions.append({
                    'id': item['id'],
                    'language': snippet['language'],
                    'name': snippet['name'],
                    'track_kind': snippet.get('trackKind', 'standard'),
                })

            return captions

        except Exception as e:
            logger.error(f"Error getting captions for video {video_id}: {e}")
            return []

    def get_api_quota_info(self) -> Dict:
        """Informations sur l'utilisation du quota API (estimation)"""
        # Les coûts approximatifs par opération
        costs = {
            'videos': 1,
            'playlists': 1,
            'playlistItems': 1,
            'channels': 1,
            'search': 100,
            'captions': 50
        }

        # Dans un vrai scénario, vous pourriez tracker ces métriques
        return {
            'daily_limit': 10000,  # Quota quotidien par défaut
            'costs': costs,
            'recommendation': 'Monitor API usage in Google Cloud Console'
        }


# Classe utilitaire pour les conversions
class YouTubeUtils:
    """Utilitaires pour manipuler les données YouTube"""

    @staticmethod
    def duration_seconds_to_human(seconds: int) -> str:
        """Convertit des secondes en format lisible (HH:MM:SS)"""
        if seconds < 3600:  # Moins d'une heure
            return f"{seconds // 60:02d}:{seconds % 60:02d}"
        else:
            hours = seconds // 3600
            minutes = (seconds % 3600) // 60
            secs = seconds % 60
            return f"{hours:02d}:{minutes:02d}:{secs:02d}"

    @staticmethod
    def format_view_count(count: int) -> str:
        """Formate le nombre de vues de manière lisible"""
        if count >= 1_000_000:
            return f"{count / 1_000_000:.1f}M"
        elif count >= 1_000:
            return f"{count / 1_000:.1f}K"
        else:
            return str(count)

    @staticmethod
    def generate_embed_url(video_id: str, **params) -> str:
        """Génère une URL d'intégration YouTube avec paramètres personnalisés"""
        base_url = f"https://www.youtube.com/embed/{video_id}"

        # Paramètres par défaut recommandés
        default_params = {
            'rel': '0',  # Ne pas montrer de vidéos connexes
            'modestbranding': '1',  # Logo YouTube discret
            'controls': '1',  # Afficher les contrôles
            'showinfo': '0',  # Masquer les infos vidéo
        }

        # Fusionner avec les paramètres personnalisés
        default_params.update(params)

        # Construire la query string
        query_parts = [f"{k}={v}" for k, v in default_params.items()]

        if query_parts:
            return f"{base_url}?{'&'.join(query_parts)}"

        return base_url

    @staticmethod
    def extract_text_from_description(description: str, max_length: int = 500) -> str:
        """Extrait et nettoie le texte d'une description YouTube"""
        if not description:
            return ""

        # Supprimer les liens
        import re
        text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '',
                      description)

        # Supprimer les caractères spéciaux excessifs
        text = re.sub(r'[^\w\s\-.,!?()"]', ' ', text)

        # Nettoyer les espaces multiples
        text = re.sub(r'\s+', ' ', text).strip()

        # Tronquer si nécessaire
        if len(text) > max_length:
            text = text[:max_length].rsplit(' ', 1)[0] + '...'

        return text