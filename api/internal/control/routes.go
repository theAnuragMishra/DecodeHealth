package control

import (
	"github.com/go-chi/chi/v5"
	"github.com/go-chi/cors"
)

func (c *Controller) SetUpRouter() {
	c.router.Use(cors.Handler(cors.Options{
		AllowedOrigins:   []string{"https://*", "http://*"},
		AllowedMethods:   []string{"GET", "POST", "PUT", "DELETE", "OPTIONS"},
		AllowedHeaders:   []string{"Accept", "Authorization", "Content-Type", "X-CSRF-Token"},
		ExposedHeaders:   []string{"Link"},
		AllowCredentials: true,
		MaxAge:           300,
	}))

	c.router.Group(func(r chi.Router) {
		r.Use(c.AuthMiddleware)
		r.Post("/new-request", c.CreateRequest)
		r.Patch("/ff-req", c.MarkRequestFulfilled)
		r.Patch("/deny-req", c.MarkRequestDenied)
		r.Patch("/acc-req", c.MarkRequestAccepted)
		r.Get("/requests-lab/{id}", c.GetRequestsForLab)
		r.Get("/requests-hospital/{id}", c.GetRequestsForHospitals)
		r.Get("/lab-list", c.GetLabs)
		r.Get("/me", c.HandleMe)
		r.Post("/logout", c.HandleLogout)
	})
	c.router.Post("/new-org", c.SignUpHandler)
	c.router.Post("/login", c.LoginHandler)
}
