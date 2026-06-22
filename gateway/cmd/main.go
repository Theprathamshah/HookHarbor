package main

import (
	"log"
	"net/http"

	"github.com/gin-gonic/gin"
)

func main() {
	r := gin.Default()

	// Health Check
	r.GET("/health", func(c *gin.Context) {
		c.JSON(http.StatusOK, gin.H{"status": "healthy"})
	})

	// Ingestion Route
	r.POST("/v1/webhooks/:endpoint_id", func(c *gin.Context) {
		endpointID := c.Param("endpoint_id")
		apiKey := c.GetHeader("X-HookHarbor-Key")

		if apiKey == "" {
			c.JSON(http.StatusUnauthorized, gin.H{"error": "Missing X-HookHarbor-Key header"})
			return
		}

		// TODO: Validate API Key and endpoint configs
		// TODO: Publish to RabbitMQ

		log.Printf("Received webhook for endpoint %s", endpointID)

		c.JSON(http.StatusAccepted, gin.H{
			"status":      "accepted",
			"endpoint_id": endpointID,
		})
	})

	log.Println("Starting Go Ingestion Gateway on :8080...")
	if err := r.Run(":8080"); err != nil {
		log.Fatalf("Failed to run gateway server: %v", err)
	}
}
