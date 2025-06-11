-- Criação da tabela para armazenar os preços do Bitcoin
CREATE TABLE IF NOT EXISTS bitcoin_prices (
    id SERIAL PRIMARY KEY,
    price DECIMAL(15, 2) NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    source VARCHAR(50) DEFAULT 'binance',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Índice para otimizar consultas por timestamp
CREATE INDEX IF NOT EXISTS idx_bitcoin_prices_timestamp ON bitcoin_prices(timestamp);

-- Índice para consultas mais recentes
CREATE INDEX IF NOT EXISTS idx_bitcoin_prices_created_at ON bitcoin_prices(created_at DESC);
