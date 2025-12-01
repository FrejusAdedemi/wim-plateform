# apps/youtube/services.py
"""
Service YouTube pour intégrer l'API YouTube Data v3
Avec filtrage des vidéos embeddable uniquement
"""

from googleapiclient.discovery import build
from django.conf import settings
import isodate
import logging

logger = logging.getLogger(__name__)


class YouTubeService:
    """Service principal pour interagir avec l'API YouTube"""

    def __init__(self):
        self.api_key = getattr(settings, 'YOUTUBE_API_KEY', '')

        if not self.api_key:
            raise Exception("YOUTUBE_API_KEY non configurée dans settings.py")

        try:
            self.youtube = build('youtube', 'v3', developerKey=self.api_key)
            print("✅ Service YouTube initialisé avec succès")
        except Exception as e:
            raise Exception(f"❌ Erreur d'initialisation YouTube: {e}")

    def get_video_details(self, video_id):
        """
        Récupère les détails d'une vidéo YouTube
        Vérifie que la vidéo est embeddable
        """
        try:
            request = self.youtube.videos().list(
                part='snippet,contentDetails,statistics,status',
                id=video_id
            )
            response = request.execute()

            if not response.get('items'):
                return None

            video = response['items'][0]
            snippet = video['snippet']
            content_details = video['contentDetails']
            statistics = video['statistics']
            status = video.get('status', {})

            # ✅ VÉRIFIER SI LA VIDÉO EST EMBEDDABLE
            is_embeddable = status.get('embeddable', False)

            if not is_embeddable:
                logger.warning(f"⚠️ Vidéo {video_id} non embeddable, ignorée")
                return None

            # Convertir la durée ISO 8601 en secondes
            duration_iso = content_details.get('duration', 'PT0S')
            duration_seconds = int(isodate.parse_duration(duration_iso).total_seconds())

            return {
                'id': video_id,
                'title': snippet['title'],
                'description': snippet.get('description', ''),
                'thumbnail_url': snippet['thumbnails']['high']['url'],
                'duration_seconds': duration_seconds,
                'view_count': int(statistics.get('viewCount', 0)),
                'channel_name': snippet['channelTitle'],
                'published_at': snippet['publishedAt'],
                'embeddable': is_embeddable
            }

        except Exception as e:
            logger.error(f"Erreur récupération vidéo {video_id}: {e}")
            return None

    def search_videos(self, query, max_results=10):
        """
        Recherche des vidéos sur YouTube
        Filtre uniquement les vidéos embeddable
        """
        try:
            request = self.youtube.search().list(
                part='snippet',
                q=query,
                maxResults=max_results,
                type='video',
                videoEmbeddable='true',  # ✅ FILTRE EMBEDDABLE
                order='relevance'
            )
            response = request.execute()

            items = response.get('items', [])
            print(f"✅ {len(items)} vidéos embeddable trouvées pour '{query}'")

            return items

        except Exception as e:
            logger.error(f"Erreur lors de la recherche '{query}': {e}")
            return []

    def get_playlist_videos(self, playlist_id, max_results=50):
        """
        Récupère les vidéos d'une playlist YouTube
        Filtre uniquement les vidéos embeddable
        """
        try:
            all_videos = []
            next_page_token = None
            skipped_count = 0

            while len(all_videos) < max_results:
                request = self.youtube.playlistItems().list(
                    part='snippet',
                    playlistId=playlist_id,
                    maxResults=min(50, max_results * 2),  # Récupérer plus pour compenser les vidéos non embeddable
                    pageToken=next_page_token
                )
                response = request.execute()

                if not response.get('items'):
                    break

                # Extraire les IDs des vidéos
                video_ids = [item['snippet']['resourceId']['videoId'] for item in response['items']]

                # Récupérer les détails de chaque vidéo (avec vérification embeddable)
                for video_id in video_ids:
                    if len(all_videos) >= max_results:
                        break

                    video_details = self.get_video_details(video_id)
                    if video_details:
                        all_videos.append(video_details)
                    else:
                        skipped_count += 1

                next_page_token = response.get('nextPageToken')
                if not next_page_token:
                    break

            if skipped_count > 0:
                print(f"⚠️ {skipped_count} vidéos non embeddable ignorées")

            return all_videos[:max_results]

        except Exception as e:
            logger.error(f"Erreur playlist {playlist_id}: {e}")
            return []

    def get_playlist_details(self, playlist_id):
        """Récupère les détails d'une playlist"""
        try:
            request = self.youtube.playlists().list(
                part='snippet,contentDetails',
                id=playlist_id
            )
            response = request.execute()

            if not response.get('items'):
                return None

            playlist = response['items'][0]
            snippet = playlist['snippet']
            content_details = playlist['contentDetails']

            return {
                'id': playlist_id,
                'title': snippet['title'],
                'description': snippet.get('description', ''),
                'video_count': content_details['itemCount'],
                'thumbnail_url': snippet['thumbnails']['high']['url'],
                'channel_name': snippet['channelTitle']
            }

        except Exception as e:
            logger.error(f"Erreur playlist details {playlist_id}: {e}")
            return None