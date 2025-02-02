import pytest
import httpx

# Base URL of the local FastAPI app
BASE_URL = "http://127.0.0.1:8000"

@pytest.fixture
def client():
    """Creates an HTTP client for testing."""
    with httpx.Client(base_url=BASE_URL) as client:
        yield client

def test_home(client):
    """Test if the home endpoint is accessible."""
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()

def test_pnl(client):
    """Test the PnL endpoint for a strategy."""
    strategy_id = "strategy_1"
    response = client.get(f"/pnl/{strategy_id}")

    assert response.status_code == 200
    data = response.json()

    assert "strategy" in data
    assert "value" in data
    assert "unit" in data
    assert "capture_time" in data

    assert data["strategy"] == strategy_id
    assert isinstance(data["value"], (int, float))
    assert data["unit"] == "euro"

def test_buy_volume(client):
    """Test the buy volume endpoint."""
    response = client.get("/volume/buy")

    assert response.status_code == 200
    data = response.json()

    assert "total_buy_volume" in data
    assert "unit" in data
    assert isinstance(data["total_buy_volume"], (int, float))
    assert data["unit"] == "MW"

def test_sell_volume(client):
    """Test the sell volume endpoint."""
    response = client.get("/volume/sell")

    assert response.status_code == 200
    data = response.json()

    assert "total_sell_volume" in data
    assert "unit" in data
    assert isinstance(data["total_sell_volume"], (int, float))
    assert data["unit"] == "MW"