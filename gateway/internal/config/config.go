package config

import "os"

type Config struct {
	Port         string
	RabbitMQURL  string
	RedisURL     string
}

func Load() *Config {
	return &Config{
		Port:        getEnv("PORT", "8080"),
		RabbitMQURL: getEnv("RABBITMQ_URL", "amqp://guest:guest@localhost:5672/"),
		RedisURL:    getEnv("REDIS_URL", "redis://localhost:6379/0"),
	}
}

func getEnv(key, defaultVal string) string {
	if value, exists := os.LookupEnv(key); exists {
		return value
	}
	return defaultVal
}
