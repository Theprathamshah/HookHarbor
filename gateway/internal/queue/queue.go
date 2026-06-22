package queue

import (
	"context"
	"log"

	amqp "github.com/rabbitmq/amqp091-go"
)

type RabbitPublisher struct {
	conn    *amqp.Connection
	channel *amqp.Channel
}

func NewRabbitPublisher(url string) (*RabbitPublisher, error) {
	conn, err := amqp.Dial(url)
	if err != nil {
		return nil, err
	}

	ch, err := conn.Channel()
	if err != nil {
		conn.Close()
		return nil, err
	}

	return &RabbitPublisher{
		conn:    conn,
		channel: ch,
	}, nil
}

func (p *RabbitPublisher) Publish(ctx context.Context, exchange, routingKey string, body []byte) error {
	log.Printf("Publishing message to exchange %s with routing key %s", exchange, routingKey)
	return p.channel.PublishWithContext(ctx,
		exchange,
		routingKey,
		false, // mandatory
		false, // immediate
		amqp.Publishing{
			ContentType: "application/json",
			Body:        body,
		},
	)
}

func (p *RabbitPublisher) Close() {
	if p.channel != nil {
		p.channel.Close()
	}
	if p.conn != nil {
		p.conn.Close()
	}
}
