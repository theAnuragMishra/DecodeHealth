package control

import (
	"log"
	"net/http"

	"github.com/go-chi/chi/v5"
	"github.com/gorilla/websocket"
	"github.com/theAnuragMishra/decode-health/api/internal/database"
)

var upgrader = websocket.Upgrader{
	ReadBufferSize:  1024,
	WriteBufferSize: 1024,
	CheckOrigin:     func(r *http.Request) bool { return true },
}

func (c *Controller) setUpSocket(router *chi.Mux) {
	router.Get("/ws", func(w http.ResponseWriter, r *http.Request) {
		conn, err := upgrader.Upgrade(w, r, nil)
		if err != nil {
			log.Println(err)
		}
		session := r.Context().Value(MiddlewareSentSession).(database.Session)
		client := NewClient(conn, c.manager, session.OrgID)
		// Add the newly created client to the manager
		c.manager.addClient(session.OrgID, client)

		// for _, client := range m.clients {
		// 	fmt.Println(client.UserID)
		// }

		// Start the read / write processes
		go client.readMessages()
		go client.writeMessages()
	})
}
