import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


# =============================================================================
# ======================== ТЕСТЫ РЕГИСТРАЦИИ ПОЛЬЗОВАТЕЛЕЙ ====================
# =============================================================================

class TestUserRegistration:
    """Тесты регистрации пользователей"""

    def test_register_user_success(self):
        """Успешная регистрация нового пользователя"""
        response = client.post("/api/users/register", json={
            "login": "user_test_1",
            "password": "password123",
            "first_name": "Ivan",
            "last_name": "Ivanov"
        })
        assert response.status_code == 201
        data = response.json()
        assert data["login"] == "user_test_1"
        assert data["first_name"] == "Ivan"
        assert data["last_name"] == "Ivanov"
        assert "id" in data
        assert "password" not in data  # Пароль не должен возвращаться

    def test_register_user_duplicate_login(self):
        """Ошибка при регистрации с существующим логином"""
        # Сначала регистрируем пользователя
        client.post("/api/users/register", json={
            "login": "duplicate_user",
            "password": "password123",
            "first_name": "Petr",
            "last_name": "Petrov"
        })

        # Пытаемся зарегистрировать ещё раз с тем же логином
        response = client.post("/api/users/register", json={
            "login": "duplicate_user",
            "password": "password456",
            "first_name": "Alex",
            "last_name": "Alexeev"
        })
        assert response.status_code == 400
        assert "already registered" in response.json()["detail"].lower()

    def test_register_user_missing_fields(self):
        """Ошибка при регистрации с отсутствующими полями"""
        response = client.post("/api/users/register", json={
            "login": "incomplete_user"
            # Отсутствуют password, first_name, last_name
        })
        assert response.status_code == 422  # Validation Error

    def test_register_user_empty_password(self):
        """Ошибка при регистрации с пустым паролем"""
        response = client.post("/api/users/register", json={
            "login": "empty_pass_user",
            "password": "",
            "first_name": "Test",
            "last_name": "Testov"
        })
        assert response.status_code == 422


# =============================================================================
# =========================== ТЕСТЫ АВТОРИЗАЦИИ (LOGIN) =======================
# =============================================================================

class TestUserLogin:
    """Тесты авторизации пользователей"""

    def test_login_success(self):
        """Успешный вход пользователя"""
        # Сначала регистрируем
        client.post("/api/users/register", json={
            "login": "login_test_user",
            "password": "secure_password",
            "first_name": "Maria",
            "last_name": "Sidorova"
        })

        # Логинимся
        response = client.post("/api/users/login", data={
            "username": "login_test_user",
            "password": "secure_password"
        })
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_login_wrong_password(self):
        """Ошибка при неверном пароле"""
        # Регистрируем пользователя
        client.post("/api/users/register", json={
            "login": "wrong_pass_user",
            "password": "correct_password",
            "first_name": "Test",
            "last_name": "Testov"
        })

        # Пытаемся войти с неправильным паролем
        response = client.post("/api/users/login", data={
            "username": "wrong_pass_user",
            "password": "wrong_password"
        })
        assert response.status_code == 401
        assert "incorrect" in response.json()["detail"].lower()

    def test_login_nonexistent_user(self):
        """Ошибка при входе несуществующего пользователя"""
        response = client.post("/api/users/login", data={
            "username": "nonexistent_user",
            "password": "any_password"
        })
        assert response.status_code == 401


# =============================================================================
# ======================== ТЕСТЫ ПОИСКА ПОЛЬЗОВАТЕЛЕЙ =========================
# =============================================================================

class TestUserSearch:
    """Тесты поиска пользователей"""

    def test_search_by_login_success(self):
        """Успешный поиск пользователя по логину"""
        # Создаём тестового пользователя
        client.post("/api/users/register", json={
            "login": "search_login_test",
            "password": "password123",
            "first_name": "Search",
            "last_name": "Test"
        })

        # Ищем по логину
        response = client.get("/api/users/search/login?login=search_login")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
        assert any(u["login"] == "search_login_test" for u in data)

    def test_search_by_login_not_found(self):
        """Поиск по логину не нашёл результатов"""
        response = client.get("/api/users/search/login?login=nonexistent_login_xyz")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0

    def test_search_by_name_success(self):
        """Успешный поиск пользователя по имени"""
        # Создаём тестового пользователя
        client.post("/api/users/register", json={
            "login": "search_name_user",
            "password": "password123",
            "first_name": "Alexander",
            "last_name": "Popov"
        })

        # Ищем по имени
        response = client.get("/api/users/search/name?name=Alexander")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1

    def test_search_by_surname_success(self):
        """Успешный поиск пользователя по фамилии"""
        response = client.get("/api/users/search/name?surname=Popov")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_search_by_name_and_surname(self):
        """Поиск по имени и фамилии одновременно"""
        response = client.get("/api/users/search/name?name=Alexander&surname=Popov")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_search_empty_query(self):
        """Поиск с пустыми параметрами (должен вернуть всех или пустой список)"""
        response = client.get("/api/users/search/name")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)


# =============================================================================
# ======================== ТЕСТЫ ПОСЫЛОК (PARCELS) ============================
# =============================================================================

class TestParcels:
    """Тесты работы с посылками"""

    def _get_auth_token(self, login, password):
        """Вспомогательная функция для получения токена"""
        response = client.post("/api/users/login", data={
            "username": login,
            "password": password
        })
        return response.json()["access_token"]

    def test_create_parcel_success(self):
        """Успешное создание посылки"""
        # Регистрируем и логинимся
        client.post("/api/users/register", json={
            "login": "parcel_owner",
            "password": "password123",
            "first_name": "Parcel",
            "last_name": "Owner"
        })
        token = self._get_auth_token("parcel_owner", "password123")

        # Создаём посылку
        response = client.post("/api/parcels", json={
            "description": "Test package",
            "weight": 2.5
        }, headers={"Authorization": f"Bearer {token}"})

        assert response.status_code == 201
        data = response.json()
        assert data["description"] == "Test package"
        assert data["weight"] == 2.5
        assert "id" in data
        assert "owner_id" in data

    def test_create_parcel_unauthorized(self):
        """Ошибка создания посылки без авторизации"""
        response = client.post("/api/parcels", json={
            "description": "Unauthorized package",
            "weight": 1.0
        })
        assert response.status_code == 401

    def test_create_parcel_invalid_weight(self):
        """Ошибка создания посылки с невалидным весом"""
        token = self._get_auth_token("parcel_owner", "password123")

        response = client.post("/api/parcels", json={
            "description": "Invalid weight package",
            "weight": -5.0  # Отрицательный вес
        }, headers={"Authorization": f"Bearer {token}"})

        assert response.status_code == 422

    def test_create_parcel_missing_fields(self):
        """Ошибка создания посылки с отсутствующими полями"""
        token = self._get_auth_token("parcel_owner", "password123")

        response = client.post("/api/parcels", json={
            "description": "Missing weight"
            # Отсутствует weight
        }, headers={"Authorization": f"Bearer {token}"})

        assert response.status_code == 422

    def test_get_my_parcels_success(self):
        """Успешное получение списка своих посылок"""
        token = self._get_auth_token("parcel_owner", "password123")

        # Сначала создаём посылку
        client.post("/api/parcels", json={
            "description": "My package",
            "weight": 1.0
        }, headers={"Authorization": f"Bearer {token}"})

        # Получаем список посылок
        response = client.get("/api/parcels/me", headers={"Authorization": f"Bearer {token}"})

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1

    def test_get_my_parcels_unauthorized(self):
        """Ошибка получения посылок без авторизации"""
        response = client.get("/api/parcels/me")
        assert response.status_code == 401


# =============================================================================
# ======================== ТЕСТЫ ДОСТАВОК (DELIVERIES) ========================
# =============================================================================

class TestDeliveries:
    """Тесты работы с доставками"""

    def _get_auth_token(self, login, password):
        """Вспомогательная функция для получения токена"""
        response = client.post("/api/users/login", data={
            "username": login,
            "password": password
        })
        return response.json()["access_token"]

    def _create_test_users(self):
        """Создаёт двух тестовых пользователей и возвращает их ID и токены"""
        # Отправитель
        client.post("/api/users/register", json={
            "login": "sender_test",
            "password": "password123",
            "first_name": "Sender",
            "last_name": "Testov"
        })
        sender_token = self._get_auth_token("sender_test", "password123")

        # Получатель
        client.post("/api/users/register", json={
            "login": "recipient_test",
            "password": "password123",
            "first_name": "Recipient",
            "last_name": "Testov"
        })
        recipient_response = client.get("/api/users/search/login?login=recipient_test")
        recipient_id = recipient_response.json()[0]["id"]

        return sender_token, recipient_id

    def test_create_delivery_success(self):
        """Успешное создание доставки"""
        sender_token, recipient_id = self._create_test_users()

        # Создаём посылку
        parcel_response = client.post("/api/parcels", json={
            "description": "Delivery test package",
            "weight": 3.0
        }, headers={"Authorization": f"Bearer {sender_token}"})
        parcel_id = parcel_response.json()["id"]

        # Создаём доставку
        response = client.post("/api/deliveries", json={
            "parcel_id": parcel_id,
            "recipient_id": recipient_id
        }, headers={"Authorization": f"Bearer {sender_token}"})

        assert response.status_code == 201
        data = response.json()
        assert data["parcel_id"] == parcel_id
        assert data["recipient_id"] == recipient_id
        assert "sender_id" in data
        assert "id" in data

    def test_create_delivery_unauthorized(self):
        """Ошибка создания доставки без авторизации"""
        response = client.post("/api/deliveries", json={
            "parcel_id": 1,
            "recipient_id": 2
        })
        assert response.status_code == 401

    def test_create_delivery_nonexistent_parcel(self):
        """Ошибка создания доставки с несуществующей посылкой"""
        sender_token, recipient_id = self._create_test_users()

        response = client.post("/api/deliveries", json={
            "parcel_id": 99999,  # Несуществующий ID
            "recipient_id": recipient_id
        }, headers={"Authorization": f"Bearer {sender_token}"})

        assert response.status_code == 404
        assert "parcel not found" in response.json()["detail"].lower()

    def test_create_delivery_nonexistent_recipient(self):
        """Ошибка создания доставки с несуществующим получателем"""
        sender_token, _ = self._create_test_users()

        # Создаём посылку
        parcel_response = client.post("/api/parcels", json={
            "description": "Test package",
            "weight": 1.0
        }, headers={"Authorization": f"Bearer {sender_token}"})
        parcel_id = parcel_response.json()["id"]

        response = client.post("/api/deliveries", json={
            "parcel_id": parcel_id,
            "recipient_id": 99999  # Несуществующий ID
        }, headers={"Authorization": f"Bearer {sender_token}"})

        assert response.status_code == 404
        assert "recipient not found" in response.json()["detail"].lower()

    def test_create_delivery_wrong_owner(self):
        """Ошибка создания доставки с чужой посылкой"""
        # Создаём двух пользователей
        sender_token, recipient_id = self._create_test_users()

        # Создаём второго отправителя
        client.post("/api/users/register", json={
            "login": "other_sender",
            "password": "password123",
            "first_name": "Other",
            "last_name": "Sender"
        })
        other_token = self._get_auth_token("other_sender", "password123")

        # Первый пользователь создаёт посылку
        parcel_response = client.post("/api/parcels", json={
            "description": "My package",
            "weight": 1.0
        }, headers={"Authorization": f"Bearer {sender_token}"})
        parcel_id = parcel_response.json()["id"]

        # Второй пользователь пытается создать доставку с чужой посылкой
        response = client.post("/api/deliveries", json={
            "parcel_id": parcel_id,
            "recipient_id": recipient_id
        }, headers={"Authorization": f"Bearer {other_token}"})

        assert response.status_code == 403
        assert "don't own" in response.json()["detail"].lower()

    def test_get_deliveries_by_sender(self):
        """Успешное получение доставок по отправителю"""
        sender_token, recipient_id = self._create_test_users()

        # Создаём посылку и доставку
        parcel_response = client.post("/api/parcels", json={
            "description": "Sender test",
            "weight": 1.0
        }, headers={"Authorization": f"Bearer {sender_token}"})
        parcel_id = parcel_response.json()["id"]

        client.post("/api/deliveries", json={
            "parcel_id": parcel_id,
            "recipient_id": recipient_id
        }, headers={"Authorization": f"Bearer {sender_token}"})

        # Получаем ID отправителя
        sender_response = client.get("/api/users/search/login?login=sender_test")
        sender_id = sender_response.json()[0]["id"]

        # Получаем доставки по отправителю
        response = client.get(f"/api/deliveries/sender/{sender_id}")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1

    def test_get_deliveries_by_recipient(self):
        """Успешное получение доставок по получателю"""
        sender_token, recipient_id = self._create_test_users()

        # Создаём посылку и доставку
        parcel_response = client.post("/api/parcels", json={
            "description": "Recipient test",
            "weight": 1.0
        }, headers={"Authorization": f"Bearer {sender_token}"})
        parcel_id = parcel_response.json()["id"]

        client.post("/api/deliveries", json={
            "parcel_id": parcel_id,
            "recipient_id": recipient_id
        }, headers={"Authorization": f"Bearer {sender_token}"})

        # Получаем доставки по получателю
        response = client.get(f"/api/deliveries/recipient/{recipient_id}")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1

    def test_get_deliveries_empty_list(self):
        """Получение пустого списка доставок"""
        response = client.get("/api/deliveries/sender/99999")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0


# =============================================================================
# ======================== ТЕСТЫ ОБРАБОТКИ ОШИБОК =============================
# =============================================================================

class TestErrorHandling:
    """Тесты обработки ошибок"""

    def test_invalid_json_body(self):
        """Ошибка при невалидном JSON"""
        response = client.post(
                "/api/users/register",
                content=b"{invalid json}",  # ← сырые байты, невалидный JSON
                headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 422

    def test_invalid_http_method(self):
        """Ошибка при неверном HTTP методе"""
        response = client.put("/api/users/register", json={
            "login": "test",
            "password": "test",
            "first_name": "Test",
            "last_name": "Test"
        })
        assert response.status_code == 405  # Method Not Allowed

    def test_nonexistent_endpoint(self):
        """Ошибка при запросе несуществующего endpoint"""
        response = client.get("/api/nonexistent/endpoint")
        assert response.status_code == 404

    def test_invalid_token_format(self):
        """Ошибка при неверном формате токена"""
        response = client.get("/api/parcels/me", headers={
            "Authorization": "Bearer invalid_token_format_xyz"
        })
        assert response.status_code == 401

    def test_missing_authorization_header(self):
        """Ошибка при отсутствии заголовка авторизации"""
        response = client.get("/api/parcels/me")
        assert response.status_code == 401


# =============================================================================
# ======================== ИНТЕГРАЦИОННЫЕ ТЕСТЫ ===============================
# =============================================================================

class TestIntegration:
    """Интеграционные тесты полного сценария"""

    def test_full_delivery_workflow(self):
        """Полный сценарий: регистрация → посылка → доставка → проверка"""
        # 1. Регистрация отправителя
        sender_response = client.post("/api/users/register", json={
            "login": "integration_sender",
            "password": "password123",
            "first_name": "Integration",
            "last_name": "Sender"
        })
        assert sender_response.status_code == 201
        sender_id = sender_response.json()["id"]

        # 2. Регистрация получателя
        recipient_response = client.post("/api/users/register", json={
            "login": "integration_recipient",
            "password": "password123",
            "first_name": "Integration",
            "last_name": "Recipient"
        })
        assert recipient_response.status_code == 201
        recipient_id = recipient_response.json()["id"]

        # 3. Логин отправителя
        login_response = client.post("/api/users/login", data={
            "username": "integration_sender",
            "password": "password123"
        })
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]

        # 4. Создание посылки
        parcel_response = client.post("/api/parcels", json={
            "description": "Integration test package",
            "weight": 5.0
        }, headers={"Authorization": f"Bearer {token}"})
        assert parcel_response.status_code == 201
        parcel_id = parcel_response.json()["id"]

        # 5. Создание доставки
        delivery_response = client.post("/api/deliveries", json={
            "parcel_id": parcel_id,
            "recipient_id": recipient_id
        }, headers={"Authorization": f"Bearer {token}"})
        assert delivery_response.status_code == 201
        delivery_id = delivery_response.json()["id"]

        # 6. Проверка доставки у отправителя
        sender_deliveries = client.get(f"/api/deliveries/sender/{sender_id}")
        assert sender_deliveries.status_code == 200
        assert any(d["id"] == delivery_id for d in sender_deliveries.json())

        # 7. Проверка доставки у получателя
        recipient_deliveries = client.get(f"/api/deliveries/recipient/{recipient_id}")
        assert recipient_deliveries.status_code == 200
        assert any(d["id"] == delivery_id for d in recipient_deliveries.json())

        # 8. Проверка посылок отправителя
        parcels = client.get("/api/parcels/me", headers={
            "Authorization": f"Bearer {token}"
        })
        assert parcels.status_code == 200
        assert any(p["id"] == parcel_id for p in parcels.json())

    def test_multiple_parcels_and_deliveries(self):
        """Тест с несколькими посылками и доставками"""
        # Регистрация
        client.post("/api/users/register", json={
            "login": "multi_sender",
            "password": "password123",
            "first_name": "Multi",
            "last_name": "Sender"
        })
        client.post("/api/users/register", json={
            "login": "multi_recipient",
            "password": "password123",
            "first_name": "Multi",
            "last_name": "Recipient"
        })

        token_response = client.post("/api/users/login", data={
            "username": "multi_sender",
            "password": "password123"
        })
        token = token_response.json()["access_token"]

        recipient_response = client.get("/api/users/search/login?login=multi_recipient")
        recipient_id = recipient_response.json()[0]["id"]

        # Создаём 3 посылки
        parcel_ids = []
        for i in range(3):
            parcel_response = client.post("/api/parcels", json={
                "description": f"Package {i}",
                "weight": float(i + 1)
            }, headers={"Authorization": f"Bearer {token}"})
            parcel_ids.append(parcel_response.json()["id"])

        # Создаём 3 доставки
        for parcel_id in parcel_ids:
            delivery_response = client.post("/api/deliveries", json={
                "parcel_id": parcel_id,
                "recipient_id": recipient_id
            }, headers={"Authorization": f"Bearer {token}"})
            assert delivery_response.status_code == 201

        # Проверяем количество посылок
        parcels_response = client.get("/api/parcels/me", headers={
            "Authorization": f"Bearer {token}"
        })
        assert len(parcels_response.json()) == 3