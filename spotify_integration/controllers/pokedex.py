from odoo import http
from odoo.http import request
import requests


class PokemonController(http.Controller):
    POKEAPI_BASE_URL = "https://pokeapi.co/api/v2"

    @http.route(['/pokemon'], type='http', auth="public", website=True)
    def pokemon_list(self, page=1, rarity=None, **kwargs):
        limit = 8
        offset = (page - 1) * limit

        # Obtener tipos (rareza) desde la API
        types_response = requests.get(f"{self.POKEAPI_BASE_URL}/type").json()
        types_list = [t['name'] for t in types_response.get('results', [])]

        # Obtener lista de Pokémon
        response = requests.get(f"{self.POKEAPI_BASE_URL}/pokemon?limit=100").json()
        pokemon_results = response.get("results", [])

        # Filtrar por tipo (rareza)
        if rarity and rarity != "All":
            filtered_pokemon = []
            for pokemon in pokemon_results:
                pokemon_data = requests.get(pokemon['url']).json()
                pokemon_types = [t['type']['name'] for t in pokemon_data['types']]
                if rarity.lower() in pokemon_types:
                    filtered_pokemon.append(pokemon)
            pokemon_results = filtered_pokemon

        # Paginación
        total_pokemons = len(pokemon_results)
        paginated_pokemons = pokemon_results[offset:offset + limit]
        total_pages = (total_pokemons + limit - 1) // limit

        return request.render('spotify_integration.pokemon_list', {
            'pokemons': paginated_pokemons,
            'page': page,
            'total_pages': total_pages,
            'types': types_list,  # Enviar tipos dinámicos
            'selected_rarity': rarity or "All",
        })

    @http.route('/pokemon/<int:pokemon_id>', type='http', auth="public", website=True)
    def pokemon_detail(self, pokemon_id, **kwargs):
        # Llamada a la API para obtener detalles del Pokémon
        pokemon_data = requests.get(f"{self.POKEAPI_BASE_URL}/pokemon/{pokemon_id}").json()
        pokemon_details = {
            'id': pokemon_data['id'],
            'name': pokemon_data['name'].capitalize(),
            'image': pokemon_data['sprites']['other']['official-artwork']['front_default'],
            'types': [t['type']['name'] for t in pokemon_data['types']],
            'stats': {stat['stat']['name']: stat['base_stat'] for stat in pokemon_data['stats']},
            'weight': pokemon_data['weight'],
            'height': pokemon_data['height'],
        }

        return request.render('spotify_integration.pokemon_detail', {
            'pokemon': pokemon_details
        })