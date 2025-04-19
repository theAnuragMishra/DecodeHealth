package control

import (
	"github.com/go-chi/chi/v5"
	"github.com/theAnuragMishra/decode-health/api/internal/database"
)

type Controller struct {
	queries *database.Queries
	router  *chi.Mux
	manager *Manager
}

func NewController(queries *database.Queries, router *chi.Mux) *Controller {
	return &Controller{queries: queries, router: router, manager: &Manager{}}
}
