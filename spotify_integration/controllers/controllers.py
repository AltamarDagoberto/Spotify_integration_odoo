from odoo import http
from odoo.http import request

class SpotifyController(http.Controller):

    @http.route('/callback', auth='public', type='http')
    def spotify_callback(self, **kwargs):
        """Recibe el 'code' de la URL de Spotify después de la autorización."""
        code = kwargs.get('code')
        if not code:
            return "Error: No se proporcionó el código de autorización."

        # Aquí buscamos la integración de Spotify para actualizar el campo authorization_code
        integration = request.env['lk.spotify'].search([('authorization_code', '=', False)], limit=1)
        if integration:
            integration.write({'authorization_code': code})
            return "Autorización exitosa. Ahora puedes obtener el token de acceso."
        else:
            return "Error: No se encontró la integración de Spotify."
