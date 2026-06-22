package handlers

import (
	"net/http"

	"github.com/gin-gonic/gin"
)

type WebhookHandler struct {
	// Add queue publisher and cache components here in future steps
}

func NewWebhookHandler() *WebhookHandler {
	return &WebhookHandler{}
}

func (h *WebhookHandler) HandleIngest(c *gin.Context) {
	endpointID := c.Param("endpoint_id")
	apiKey := c.GetHeader("X-HookHarbor-Key")

	if apiKey == "" {
		c.JSON(http.StatusUnauthorized, gin.H{"error": "Missing X-HookHarbor-Key header"})
		return
	}

	// Implementation details will go here:
	// 1. Verify API Key and check cache
	// 2. Read request body
	// 3. Publish message to RabbitMQ Main Exchange
	// 4. Return StatusAccepted

	c.JSON(http.StatusAccepted, gin.H{
		"status":      "accepted",
		"endpoint_id": endpointID,
	})
}
