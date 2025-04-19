package control

import (
	"encoding/json"
	"log"

	"github.com/gorilla/websocket"
)

type Event struct {
	Payload json.RawMessage `json:"payload"`
	Type    string          `json:"type"`
}

type Client struct {
	conn    *websocket.Conn
	egress  chan Event
	ID      int32
	manager *Manager
}

func NewClient(conn *websocket.Conn, manager *Manager, id int32) *Client {
	return &Client{
		ID:      id,
		conn:    conn,
		manager: manager,
		egress:  make(chan Event),
	}
}

func (c *Client) readMessages() {
	defer func() {
		log.Println("client disconnected ", c.ID)
		c.manager.RemoveClient(c.ID)
	}()
	for {
		_, payload, err := c.conn.ReadMessage()
		if err != nil {
			if websocket.IsUnexpectedCloseError(err, websocket.CloseGoingAway, websocket.CloseAbnormalClosure) {
				log.Println("error", err)
			}
			break
		}

		var request Event

		if err := json.Unmarshal(payload, &request); err != nil {
			log.Printf("error marshalling event %v", err)
			break
		}
		if err := routeEvent(request, c); err != nil {
			log.Println("error handling message: ", err)
		}

	}
}

func (c *Client) writeMessages() {
	defer func() {
		log.Println("Closing write connection for client:", c.ID)
		c.manager.RemoveClient(c.ID)
	}()
	for {
		select {
		case message, ok := <-c.egress:
			if !ok {
				if err := c.conn.WriteMessage(websocket.CloseMessage, nil); err != nil {
					log.Println("connection closed: ", err)
				}
				return
			}
			data, err := json.Marshal(message)
			if err != nil {
				log.Println(err)
				return
			}
			if err := c.conn.WriteMessage(websocket.TextMessage, data); err != nil {
				log.Println(err)
			}
		}
	}
}

// Send sends an event to the egress channel which is then written to the client by WriteMessage
func (c *Client) Send(event Event) {
	c.egress <- event
}
