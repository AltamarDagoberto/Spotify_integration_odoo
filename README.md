# Spotify_integration_odoo
Este módulo proporciona una integración con la API de Spotify, permitiendo a los usuarios conectar sus cuentas de Spotify a Odoo para gestionar y sincronizar playlists y canciones directamente desde el sistema.


# Funcionalidades

* Autenticación y autorización en Spotify: El módulo utiliza el flujo de autorización de Spotify para permitir que los usuarios se autentiquen y obtengan un token de acceso que les permite interactuar con la API de Spotify.

* Sincronización de Playlists: Los usuarios pueden ver, actualizar y gestionar sus playlists de Spotify directamente desde Odoo.
Creación de Playlists en Spotify: Permite la creación de nuevas playlists en Spotify desde Odoo.

* Gestión de Canciones: Sincroniza las canciones de las playlists de Spotify y las muestra en Odoo

# Modelos

# lk.spotify
Este modelo representa la integración con Spotify y contiene la información necesaria para autenticar al usuario y gestionar las playlists.

Campos:

* client_id: ID del cliente de la aplicación en Spotify.
* client_secret: Secreto del cliente para autenticar la aplicación.
* token: Token de acceso de Spotify.
* playlist_ids: Relación con las playlists asociadas a esta integración.
* authorization_code: Código de autorización de Spotify.
* name: Código único de la integración (utiliza una secuencia para generarse automáticamente).
* playlist_name: Nombre de la playlist.
  
# Métodos:

* get_access_token(): Obtiene el token de acceso de Spotify utilizando el código de autorización.
* get_authorization_url(): Genera la URL para autorizar la integración en Spotify.
* fetch_playlists(): Recupera las playlists del usuario en Spotify y las sincroniza en Odoo.
* create_playlist_in_spotify(): Crea una nueva playlist en Spotify.
* open_playlist_wizard(): Abre un wizard para crear nuevas playlists en Spotify desde Odoo.
  
# spotify.playlist
Este modelo representa una playlist en Spotify y su relación con Odoo.

Campos:

* integration_id: Relación con la integración de Spotify.
* name: Nombre de la playlist.
* spotify_id: ID único de la playlist en Spotify.
* track_ids: Relación con las canciones de la playlist.

# Métodos:

* fetch_tracks(): Obtiene las canciones de la playlist seleccionada desde Spotify y las sincroniza en Odoo.
* update_playlist_name(): Actualiza el nombre de la playlist en Spotify.
* delete_playlist_name(): Elimina la playlist de Spotify y de Odoo.

# spotify.track
Este modelo representa una canción en Spotify asociada a una playlist.

Campos:

* playlist_id: Relación con la playlist de la cual forma parte la canción.
* name: Nombre de la canción.
* spotify_id: ID único de la canción en Spotify.
  
# spotify.playlist.wizard
Este es un modelo transitorio (wizard) que permite al usuario crear nuevas playlists en Spotify desde Odoo.

Campos:

* name: Nombre de la nueva playlist.
  
# Métodos:
create_playlist(): Crea la nueva playlist en Spotify a través de la integración.
