import json
import scrapy
import pandas as pds

class PokemonScrapper(scrapy.Spider):
  name = 'pokemon_scrapper'
  domain = "https://pokemondb.net"

  start_urls = ["https://pokemondb.net/pokedex/all"]

  def parse(self, response):
    pokemons = response.css('#pokedex > tbody > tr')
    
    for pokemon in pokemons:
      link = pokemon.css("td.cell-name > a::attr(href)").extract_first()
      yield response.follow(self.domain + link, self.parse_pokemon)

  def parse_pokemon(self, response):
    data = {
      'url': response.url,
      'nome': response.css('#main > h1::text').get(),
      'numero': response.css('.vitals-table > tbody > tr:nth-child(1) > td > strong::text').get(),
      'tipos': response.css('.vitals-table > tbody > tr:nth-child(2) > td > a.type-icon::text').getall(),
      'proxima_evolucao': response.css('#main > div.infocard-list-evo > div:nth-child(3) > span.infocard-lg-data.text-muted > a::text').get(),
      'tamanho': response.css('.vitals-table > tbody > tr:nth-child(4) > td::text').get(),
      'peso': response.css('.vitals-table > tbody > tr:nth-child(5) > td::text').get(),
      'habilidades': self.get_habilidades(response)
    }

    data_frame = pds.DataFrame([data])

    # removendo a linha habilidades se for vazia
    if data_frame['habilidades'].isnull().any():
      data_frame = data_frame.drop(columns=['habilidades'])

    # removendo a linha de proxima_evolucao se for vazio
    if data_frame['proxima_evolucao'].isnull().any():
      data_frame = data_frame.drop(columns=['proxima_evolucao'])

    # removendo o \xao do tamanho e peso
    data_frame['tamanho'] = data_frame['tamanho'].str.replace('\xa0', ' ', regex=False)
    data_frame['peso'] = data_frame['peso'].str.replace('\xa0', ' ', regex=False)

    return data_frame.to_dict(orient='records')

  def get_habilidades(self, response):
    habilidades = []

    for hb in response.css('table.vitals-table .text-muted > a::attr(href)').getall():
      habilidades.append({
        'url': response.urljoin(hb),
        'nome': response.css(f'a[href="{hb}"]::text').get(),
        'descricao': response.css(f'a[href="{hb}"]::attr(title)').get(),
      })
    
    return habilidades