from clarifai_grpc.channel.clarifai_channel import ClarifaiChannel
from clarifai_grpc.grpc.api import service_pb2_grpc, service_pb2, resources_pb2
from clarifai_grpc.grpc.api.status import status_code_pb2
from random import randint
from telegram import ReplyKeyboardMarkup, KeyboardButton

import settings


def play_random_numbers(user_number):
    bot_number = randint(user_number - 10, user_number + 10)
    if user_number > bot_number:
        message = (f"Ваше число {user_number}, мое число {bot_number}, "
                   f"вы выиграли")
    elif user_number == bot_number:
        message = f"Ваше число {user_number}, мое число {bot_number}, ничья"
    else:
        message = (f"Ваше число {user_number}, мое число {bot_number}, "
                   f"вы проиграли")
    return message


def main_keyboard():
    return ReplyKeyboardMarkup([
            ['Прислать котика',
             KeyboardButton('Мои координаты', request_location=True),
             'Заполнить анкету'
             ]
        ])


def has_object_on_image(file_name, object_name):
    channel = ClarifaiChannel.get_grpc_channel()
    app = service_pb2_grpc.V2Stub(channel)
    metadata = (('authorization', f'Key {settings.CLARIFAI_API_KEY}'),)

    with open(file_name, 'rb') as f:
        file_data = f.read()
        image = resources_pb2.Image(base64=file_data)

    request = service_pb2.PostModelOutputsRequest(
        model_id='aaa03c23b3724a16a56b629203edc62c',
        inputs=[
            resources_pb2.Input(data=resources_pb2.Data(image=image))
        ])

    response = app.PostModelOutputs(request, metadata=metadata)
    # print(response)
    return check_response_for_object(response, object_name)


def check_response_for_object(response, object_name):
    if response.status.code == status_code_pb2.SUCCESS:
        for concept in response.outputs[0].data.concepts:
            if concept.name == object_name and concept.value >= 0.85:
                return True
    else:
        print(f"Ошибка распознавания: {response.outputs[0].status.details}")

    return False


if __name__ == '__main__':
    print(has_object_on_image('images/cat_2.jpg', 'cat'))
    print(has_object_on_image('images/not_cat.jpg', 'cat'))
    print(has_object_on_image('images/not_cat2.jpg', 'dog'))
