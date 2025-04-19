package control

import (
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

	c.router.Post("/new-org", c.SignUpHandler)
	c.router.Post("/login", c.LoginHandler)
	c.router.Get("/me", c.HandleMe)
	c.router.Post("/logout", c.HandleLogout)
	c.router.Post("/new-request", c.CreateRequest)
	c.router.Patch("/ff-req", c.MarkRequestFulfilled)
	c.router.Patch("/deny-req", c.MarkRequestDenied)
	c.router.Patch("/acc-req", c.MarkRequestAccepted)
	c.router.Get("/requests-lab/{id}", c.GetRequestsForLab)
	c.router.Get("/requests-hospital/{id}", c.GetRequestsForHospitals)
}
