from api import PetFriend
from settings import valid_email, valid_password, invalid_email, invalid_password
import os
import pytest
pf = PetFriend()

def test_get_api_key_for_valid_user(email=valid_email, password=valid_password):
    """ Проверяем что запрос api ключа возвращает статус 200 и в результате содержится слово key"""
    # Отправляем запрос и сохраняем полученный ответ с кодом статуса в status, а текст ответа в result
    status, result = pf.get_api_key(email, password)

    # Сверяем полученные данные с нашими ожиданиями
    assert status == 200
    assert 'key' in result

def test_get_all_pets_with_valid_key(filter=''):
    """ Проверяем что запрос всех питомцев возвращает не пустой список.
        Для этого сначала получаем api ключ и сохраняем в переменную auth_key. Далее используя этого ключ
        запрашиваем список всех питомцев и проверяем что список не пустой.
        Доступное значение параметра filter - 'my_pets' либо '' """

    _, auth_key = pf.get_api_key(valid_email, valid_password)
    status, result = pf.get_list_of_pets(auth_key, filter)
    assert status == 200
    assert len(result['pets']) > 0

def test_add_new_pet_with_valid_data(name='Кекс', animal_type='кот', age='1', pet_photo='image/cat_photo1.jpg'):
    """Проверяем что можно добавить питомца с корректными данными"""

    # Получаем полный путь изображения питомца и сохраняем в переменную pet_photo
    pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)

    # Запрашиваем ключ api и сохраняем в переменную auth_key
    _, auth_key = pf.get_api_key(valid_email, valid_password)

    # Добавляем питомца
    status, result = pf.add_new_pet(auth_key, name, animal_type, age, pet_photo)

    # Сверяем полученный ответ с ожидаемым результатом
    assert status == 200
    assert result['name'] == name

def test_successful_delete_self_pet():
    """Проверяем возможность удаления питомца"""

    # Получаем ключ auth_key и запрашиваем список своих питомцев
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_of_pets(auth_key, filter="my_pets")


    # Проверяем - если список своих питомцев пустой, то добавляем нового и опять запрашиваем список своих питомцев
    if len(my_pets['pets']) == 0:
        pf.add_new_pet(auth_key, name="Рем", animal_type="собака", age='15', pet_photo="image/dog_photo1.jpg")
        _, my_pets = pf.get_list_of_pets(auth_key, filter="my_pets")

    # Берём id первого питомца из списка и отправляем запрос на удаление
    pet_id = my_pets['pets'][0]['id']
    status, _ = pf.delete_pet(auth_key, pet_id)

    # Ещё раз запрашиваем список своих питомцев
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")
    print(my_pets)

    # Проверяем что статус ответа равен 200 и в списке питомцев нет id удалённого питомца
    assert status == 200
    assert pet_id not in my_pets.values()


def test_successful_update_self_pet_info(name='Мурзик', animal_type='Котэ', age='5'):
    """Проверяем возможность обновления информации о питомце"""

    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    if len(my_pets['pets']) > 0:
        status, result = pf.update_pet_info(auth_key, my_pets['pets'][0]['id'], name, animal_type, age)
        assert status == 200
        assert result['name'] == name
    else:
        raise Exception("There is no my pets")



def test_successful_create_new_simple(name='Коржик', animal_type='кот', age='2'):
    """Проверяем что можно добавить нового питомца без фотографии"""

    _, auth_key = pf.get_api_key(valid_email, valid_password)
    status, result = pf.add_new_pet_without_photo(auth_key, name, animal_type, age)

    # Сверяем полученный ответ с ожидаемым результатом
    assert status == 200
    assert result['name'] == name

def test_successful_add_photo(pet_photo='image/cat_photo2.jpg'):
    pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_of_pets(auth_key, filter="my_pets")

    if len(my_pets['pets']) == 0:
        pf.add_new_pet_without_photo(auth_key, name='Джоржик', animal_type='cat', age='2')
        _, my_pets = pf.get_list_of_pets(auth_key, filter="my_pets")

    pet_id = my_pets['pets'][0]['id']
    status, result = pf.add_pet_photo(auth_key, pet_id, pet_photo)

    assert status == 200
    assert 'pet_photo' in result


def test_get_api_key_for_invalid_email(email=invalid_email, password=valid_password):
    """ Проверяем что запрос api ключа c невалидным email возвращает статус 403"""
    # Отправляем запрос и сохраняем полученный ответ с кодом статуса в status, а текст ответа в result
    status, result = pf.get_api_key(email, password)

    # Сверяем полученные данные с нашими ожиданиями
    assert status == 403

def test_get_api_key_for_invalid_password(email=valid_email, password=invalid_password):
    """ Проверяем что запрос api ключа c невалидным паролем возвращает статус 403"""
    # Отправляем запрос и сохраняем полученный ответ с кодом статуса в status, а текст ответа в result
    status, result = pf.get_api_key(email, password)

    # Сверяем полученные данные с нашими ожиданиями
    assert status == 403


def test_unsuccessful_add_photo_giv_format(pet_photo='image/cat_photo4.gif'):
    '''Проверяем что нельзя добавить фото животного в фортате .gif'''
    pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_of_pets(auth_key, filter="my_pets")

    if len(my_pets['pets']) == 0:
        pf.add_new_pet_without_photo(auth_key, name='Джоржик', animal_type='cat', age='2')
        _, my_pets = pf.get_list_of_pets(auth_key, filter="my_pets")

    pet_id = my_pets['pets'][0]['id']
    status, result = pf.add_pet_photo(auth_key, pet_id, pet_photo)

    assert status != 200


def test_unsuccessful_create_pet_with_empty_name(name=None, animal_type='кот', age='2'):
    """Проверяем что нельзя добавить нового питомца без ввода имени"""

    _, auth_key = pf.get_api_key(valid_email, valid_password)
    status, result = pf.add_new_pet_without_photo(auth_key, name, animal_type, age)

    # Сверяем полученный ответ с ожидаемым результатом
    assert status == 400


def test_unsuccessful_create_pet_with_empty_animal_type(name='Kat', animal_type=None, age='2'):
    """Проверяем что нельзя добавить нового питомца без ввода вида животного"""

    _, auth_key = pf.get_api_key(valid_email, valid_password)
    status, result = pf.add_new_pet_without_photo(auth_key, name, animal_type, age)

    # Сверяем полученный ответ с ожидаемым результатом
    assert status == 400


def test_unsuccessful_create_pet_with_empty_age(name='Kat', animal_type='cat', age=None):
    """Проверяем что нельзя добавить нового питомца без ввода возраста"""

    _, auth_key = pf.get_api_key(valid_email, valid_password)
    status, result = pf.add_new_pet_without_photo(auth_key, name, animal_type, age)

    # Сверяем полученный ответ с ожидаемым результатом
    assert status == 400


def test_add_new_pet_with_non_existent_photo(name='Kat', animal_type='None', age='123456', pet_photo='image/none.jpg'):
    """Проверяем, что добавление несуществующего файла вызывают исключение"""

    _, auth_key = pf.get_api_key(valid_email, valid_password)

    try:
        status, result = pf.add_new_pet(auth_key, name, animal_type, age, pet_photo)

    except FileNotFoundError:
        assert True
    else:
        assert False



def test_unsuccessful_add_photo_svg_format(pet_photo='image/cat_photo3.svg'):
    '''Проверяем что нельзя добавить фото животного в фортате .svg'''
    pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_of_pets(auth_key, filter="my_pets")

    if len(my_pets['pets']) == 0:
        pf.add_new_pet_without_photo(auth_key, name='Джоржик', animal_type='cat', age='2')
        _, my_pets = pf.get_list_of_pets(auth_key, filter="my_pets")

    pet_id = my_pets['pets'][0]['id']
    status, result = pf.add_pet_photo(auth_key, pet_id, pet_photo)

    assert status != 200











