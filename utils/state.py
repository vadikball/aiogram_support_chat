
import abc
import json
from typing import Any, Union


class BaseStorage:
    def __init__(self, proxy: Any):
        self.proxy = proxy

    @abc.abstractmethod
    def save_state(self, state: dict) -> None:
        """Сохранить состояние в постоянное хранилище"""
        pass

    @abc.abstractmethod
    def retrieve_key(self, key: Any) -> Any:
        """Загрузить состояние локально из постоянного хранилища"""
        pass

    @abc.abstractmethod
    def retrieve_state(self) -> dict:
        """Загрузить все состояние локально из постоянного хранилища"""
        pass

    @abc.abstractmethod
    def del_state(self, key: Any) -> None:
        """Удалить состояние из постоянного хранилища"""
        pass

    @abc.abstractmethod
    def del_pairs(self, key: Any) -> None:
        """
        Удалить 2 состояния из постоянного хранилища
        Для чата с админом.
        """
        pass

    @abc.abstractmethod
    def clear_state(self) -> None:
        """
        Очистить машину состояния
        """
        pass


class JsonFileStorage(BaseStorage):
    """
        Реализация сохранения состояния
        через файловую систему.
        В self.proxy хранится путь к файлу как raw str
        """

    def retrieve_state(self) -> dict:
        try:
            with open(self.proxy) as outfile:
                state = json.load(outfile)
        except FileNotFoundError:
            state = None
        except json.decoder.JSONDecodeError:
            state = None
        return state

    def retrieve_key(self, key: str) -> dict:
        state = self.retrieve_state()
        if state is not None:
            state = state.get(key)
        return state

    def save_state(self, state: dict) -> None:
        try:
            with open(self.proxy) as outfile:
                old_state = json.load(outfile)
        except FileNotFoundError or json.decoder.JSONDecodeError:
            old_state = {}
        with open(self.proxy, 'w') as outfile:
            for key, value in state.items():
                old_state[key] = value

            json.dump(old_state, outfile)

    def del_state(self, key: Any) -> None:
        try:
            with open(self.proxy) as outfile:
                old_state = json.load(outfile)
        except FileNotFoundError or json.decoder.JSONDecodeError:
            return
        else:
            try:
                del old_state[str(key)]
            finally:
                with open(self.proxy, 'w') as outfile:
                    json.dump(old_state, outfile)

    def del_pairs(self, key: Any):
        try:
            with open(self.proxy) as outfile:
                old_state = json.load(outfile)
        except FileNotFoundError or json.decoder.JSONDecodeError:
            return
        else:
            value = old_state.get(str(key))

            self.del_state(str(key))
            self.del_state(str(value))

    def clear_state(self) -> None:
        with open(self.proxy, 'w') as outfile:
            json.dump({}, outfile)


class State:
    """
    Класс для хранения состояния при работе с данными.
    Используемые ключи в дефолтном файле:
    main_admin_chat
    appeal_chat
    suggestion_chat

    admin_dialog.json это другой файла, в котором ключи - tg id админа, значения - tg id юзера
    """

    def __init__(self, storage: BaseStorage):
        self.storage = storage

    def set_state(self, state: dict) -> None:
        """Установить состояние для определённого ключа"""
        self.storage.save_state(state)

    def get_key(self, key: str) -> Any:
        """Получить состояние по определённому ключу"""
        return self.storage.retrieve_key(key)

    def get_state(self) -> Any:
        """Получить состояние по определённому ключу"""
        return self.storage.retrieve_state()

    def del_state(self, key: Any) -> None:
        self.storage.del_state(key)

    def del_pairs(self, key: Any) -> None:
        self.storage.del_pairs(key)

    def clear_state(self):
        self.storage.clear_state()


def state_maker(protocol: Union[BaseStorage, JsonFileStorage] = JsonFileStorage,
                proxy: Any = 'state.json') -> State:
    return State(protocol(proxy))
