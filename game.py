import json


class Player:
    def __init__(self, id=None, name='', location=None, gender=''):
        self.id = id
        self.name = name
        self.location = location
        self.gender = gender
        self.quantity_location = 0
        self.time_late = 0

    def __str__(self):
        print(f'Имя:{self.name}, Id:{self.chat_id}, Gender:{self.gender}')

    def set_gender(self, new_gender):
        if new_gender.lower() == 'мужской':
            self.gender = 'Мужской'
        elif new_gender.lower() == 'женский':
            self.gender = 'Женский'


class Location:
    def __init__(self, name_location, description, available_actions):
        self.name_location = name_location
        self.description = description
        self.available_actions = available_actions


class Game:
    def __init__(self, player, json_file):
        self.player = player
        self.process_input = lambda x: str(x). \
            replace('{ending}', self.player.ending). \
            replace('{name}', self.player.name)
        self.process_output = lambda x: str(x).replace('{time}', str(
            self.player.time_late))
        self.locations = parse_json(json_file, self.process_input)
        self.player.location = self.locations['start']
        self.output = lambda x: print(self.process_output(x))

    def get_actions(self):
        actions = self.player.location.available_actions.keys()
        return list(actions)

    def output_actions(self):
        self.output('Варианты действий')
        for choice, action in enumerate(self.get_actions(), 1):
            self.output(f'{choice}, {action}')

    def take_an_action(self, action):
        self.player.quantity_location += 1
        self.player.location = self.locations[
            self.player.location.available_actions[action]]


def parse_json(filename, process_str):
    """Читает json файл с описаниями локаций
  и возвращает словарь объектов класса Location"""
    with open(filename, encoding='utf-8') as file:
        data = file.read()
        data = json.loads(data)
        all_locations = {}
        for location_name in data['locations']:
            location = data['locations'][location_name]
            all_locations[location_name] = Location(
                name_location=location_name,
                description=location['description'],
                available_actions=location['actions']
                )
        return all_locations
