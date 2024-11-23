from odoo import api, fields, models
from odoo.exceptions import ValidationError
from odoo.exceptions import UserError
import requests
import base64
import urllib
from datetime import date


class lk_spotify(models.Model):
    _name = 'lk.spotify'
    _description = 'Integración Spotify'
    _rec_name = 'name'

    client_id = fields.Char(string='Client ID', required=True)
    client_secret = fields.Char(string='Client Secret', required=True)
    token = fields.Text(string='Access Token', readonly=True)
    playlist_ids = fields.One2many('spotify.playlist', 'integration_id', string='Playlists')
    authorization_code = fields.Char(string="Authorization Code", readonly=False)
    name = fields.Char(string='Spotify Integration Code', readonly=True, copy=False)
    playlist_name = fields.Char(string="Nombre de la Playlist")

    # PARA CREAR UNA SECUENCIA
    @api.model
    def create(self, vals):
        # Asignar la secuencia al campo 'code' cuando se crea un nuevo registro
        if not vals.get('name'):
            vals['name'] = self.env['ir.sequence'].next_by_code('lk.spotify') or '/'
        return super(lk_spotify, self).create(vals)

    #FUNCION PARA OBTENER EL TOKEN DE ACCESO DEPENDIENDO A LA RUTA
    def get_access_token(self):
        redirect_uri = "http://localhost:8069/callback"
        code = self.authorization_code
        response = requests.post(
            'https://accounts.spotify.com/api/token',
            data={
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": redirect_uri
            },
            headers={
                'Authorization': 'Basic ' + base64.b64encode(f"{self.client_id}:{self.client_secret}".encode()).decode()
            }
        )

        if response.status_code == 200:
            self.token = response.json().get('access_token')
        else:
            raise ValidationError('Error al obtener el token de acceso de Spotify')

    def get_authorization_url(self):
        #Genera la URL para autorizar la aplicación en Spotify.
        self.ensure_one()
        redirect_uri = "http://localhost:8069/callback"
        scopes = "playlist-read-private user-library-read playlist-read-collaborative playlist-modify-public playlist-modify-private"

        # scopes = "playlist-read-private user-library-read playlist-read-collaborative"
        url = (
            f"https://accounts.spotify.com/authorize?"
            f"client_id={self.client_id}&"
            f"response_type=code&"
            f"redirect_uri={redirect_uri}&"
            f"scope={scopes}"
        )
        return {
            'type': 'ir.actions.act_url',
            'url': url,
            'target': 'new',
        }

    def fetch_playlists(self):
        """Obtiene las playlists del usuario utilizando el token existente."""
        # self.ensure_one()

        if not self.token:
            raise ValueError("El token no está configurado. Asegúrate de autenticar primero.")

        # self.get_access_token()

        url_user = "https://api.spotify.com/v1/me/"
        headers = {"Authorization": f"Bearer {self.token}"}

        response = requests.get(url_user, headers=headers)

        if response.status_code == 200:
            user = response.json()
            url = f'http://api.spotify.com/v1/users/{user["id"]}/playlists'
            response = requests.get(url, headers=headers)
            playlists_data = response.json()
            playlists = playlists_data.get("items", [])

            # Limpiar las playlists anteriores
            self.playlist_ids.unlink()

            for playlist in playlists:
                self.env["spotify.playlist"].create({
                    "integration_id": self.id,
                    "name": playlist.get('name'),
                    "spotify_id": playlist.get('id'),
                })
            return f"{len(playlists_data)} playlists actualizadas."
        else:
            error_message = f"Error {response.status_code}: {response.text}"
            raise ValueError("No se pudieron obtener las playlists. Revisa el token y permisos.")

    def update_playlists(self):
        """Actualiza las playlists del usuario."""
        self.ensure_one()
        if not self.token:
            self.get_access_token()

        url = 'https://api.spotify.com/v1/me/playlists'
        headers = {'Authorization': f'Bearer {self.token}'}
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            playlists_data = response.json().get('items', [])
            self.playlist_ids.unlink()  # Limpiar playlists anteriores
            for playlist in playlists_data:
                self.env['spotify.playlist'].create({
                    'integration_id': self.id,
                    'name': playlist.get('name'),
                    'spotify_id': playlist.get('id'),
                })
        else:
            raise ValueError("Error al obtener las playlists.")

    def create_playlist_in_spotify(self, playlist_name):
        """Crea una nueva playlist en Spotify."""
        self.ensure_one()
        if not self.token:
            self.get_access_token()

        # Obtener el ID del usuario de Spotify
        url_user = "https://api.spotify.com/v1/me/"
        headers = {"Authorization": f"Bearer {self.token}"}
        response = requests.get(url_user, headers=headers)

        if response.status_code == 200:
            user = response.json()
            user_id = user.get('id')

            # Crear la playlist
            url = f'https://api.spotify.com/v1/users/{user_id}/playlists'
            data = {
                'name': playlist_name,
                'public': False  # Puedes hacer la playlist pública o privada
            }

            response = requests.post(url, json=data, headers=headers)

            if response.status_code == 201:
                # Playlist creada con éxito
                playlist_data = response.json()
                self.env['spotify.playlist'].create({
                    'integration_id': self.id,
                    'name': playlist_data['name'],
                    'spotify_id': playlist_data['id'],
                })
                return "Playlist creada exitosamente en Spotify."
            else:
                raise UserError(f"Error al crear la playlist en Spotify: {response.text}")
        else:
            raise UserError(f"Error al obtener los datos del usuario de Spotify: {response.text}")


    def open_playlist_wizard(self):
        """Método para abrir el wizard de creación de playlist"""
        # Aquí se invoca el wizard (spotify.playlist.wizard)
        return {
            'name': 'Crear Playlist en Spotify',
            'type': 'ir.actions.act_window',
            'res_model': 'spotify.playlist.wizard',
            'view_mode': 'form',
            'target': 'new',  # Esto abre el wizard en una ventana modal
        }

    # CANCIIONES
class SpotifyPlaylist(models.Model):
    _name = 'spotify.playlist'
    _description = 'Playlists de Spotify'

    integration_id = fields.Many2one('lk.spotify', string='Integración', readonly=True)
    name = fields.Char(string='Nombre de la Playlist')
    spotify_id = fields.Char(string='ID de Spotify', readonly=True)
    track_ids = fields.One2many('spotify.track', 'playlist_id', string='Canciones')

    def fetch_tracks(self):
        """Obtiene las canciones de la playlist seleccionada."""
        self.ensure_one()
        integration = self.integration_id
        if not integration.token:
            integration.get_access_token()

        url = f'https://api.spotify.com/v1/playlists/{self.spotify_id}/tracks'
        headers = {'Authorization': f'Bearer {integration.token}'}
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            tracks_data = response.json().get('items', [])
            self.track_ids.unlink()  # Limpiar canciones anteriores
            for item in tracks_data:
                track = item.get('track', {})
                self.env['spotify.track'].create({
                    'playlist_id': self.id,
                    'name': track.get('name'),
                    'spotify_id': track.get('id'),
                })
        else:
            raise ValueError("Error al obtener las canciones.")

    def update_playlist_name(self):
        """Actualiza el nombre de una playlist en Spotify."""
        self.ensure_one()  # Asegura que solo hay un registro en la operación
        if not self.integration_id.token:  # Verifica si la integración tiene el token
            self.integration_id.get_access_token()  # Si no tiene token, lo obtiene

        # URL de la API de Spotify para actualizar la playlist
        url = f'https://api.spotify.com/v1/playlists/{self.spotify_id}'

        # Cabecera con el token de autorización
        headers = {'Authorization': f'Bearer {self.integration_id.token}'}

        # Datos que se envían a la API (nuevo nombre de la playlist)
        data = {'name': self.name}  # El nombre que actualizarás es el mismo campo en el modelo Odoo

        # Realizamos la solicitud PUT para actualizar la playlist
        response = requests.put(url, json=data, headers=headers)

        # Verificamos la respuesta
        if response.status_code == 200:
            # Si la respuesta es exitosa, actualizamos el nombre en Odoo
            return "Nombre de la playlist actualizado exitosamente en Spotify."
        else:
            # Si hay un error, lanzamos una excepción con el mensaje de error
            raise UserError(f"Error al actualizar el nombre de la playlist en Spotify: {response.text}")

    def delete_playlist_name(self):
        """Elimina la playlist en Spotify y también en Odoo."""
        self.ensure_one()  # Asegura que solo hay un registro en la operación
        if not self.integration_id.token:  # Verifica si la integración tiene el token
            self.integration_id.get_access_token()  # Si no tiene token, lo obtiene

        # URL de la API de Spotify para eliminar la playlist
        url = f'https://api.spotify.com/v1/playlists/{self.spotify_id}'

        # Cabecera con el token de autorización
        headers = {'Authorization': f'Bearer {self.integration_id.token}'}

        # Realizamos la solicitud DELETE para eliminar la playlist en Spotify
        response = requests.delete(url, headers=headers)

        if response.status_code == 200:
            # Si la respuesta es exitosa, eliminamos la playlist de Odoo
            self.unlink()  # Elimina el registro de la playlist en Odoo
            return "Playlist eliminada exitosamente en Spotify y Odoo."
        else:
            # Si hay un error, lanzamos una excepción con el mensaje de error
            raise UserError(f"Error al eliminar la playlist en Spotify: {response.text}")

class SpotifyTrack(models.Model):
    _name = 'spotify.track'
    _description = 'Canciones de Spotify'

    playlist_id = fields.Many2one('spotify.playlist', string='Playlist')
    name = fields.Char(string='Nombre de la Canción')
    spotify_id = fields.Char(string='ID de Spotify')

class SpotifyPlaylistWizard(models.TransientModel):
    _name = 'spotify.playlist.wizard'
    _description = 'Wizard para Crear Playlist en Spotify'

    name = fields.Char(string="Nombre de la Playlist", required=True)

    def create_playlist(self):
        """Crea la playlist en Spotify a través de la integración de lk.spotify."""
        integration = self.env['lk.spotify'].browse(self._context.get('active_id'))
        # Crear la playlist en Spotify con el nombrees
        integration.create_playlist_in_spotify(self.name)
        return {'type': 'ir.actions.act_window_close'}
