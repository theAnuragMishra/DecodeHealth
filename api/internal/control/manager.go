package control

import (
	"errors"
	"log"
	"sync"
)

type Manager struct {
	clients map[int32]*Client
	sync.RWMutex
}

func NewManager() *Manager {
	return &Manager{
		clients: make(map[int32]*Client),
	}
}

type EventHandler func(event Event, client *Client) error

var handlers map[string]EventHandler

// setting up event handlers
func (m *Manager) setupEventHandlers() {
}

func routeEvent(event Event, c *Client) error {
	if handler, ok := handlers[event.Type]; ok {
		if err := handler(event, c); err != nil {
			return err
		}
		return nil
	} else {
		return errors.New("there is no event of this type")
	}
}

func (m *Manager) addClient(id int32, client *Client) {
	// Lock so we can manipulate
	m.Lock()
	defer m.Unlock()
	log.Println("adding client")
	// Add Client
	m.clients[id] = client
}

// RemoveClient will remove the client and clean up
func (m *Manager) RemoveClient(id int32) {
	m.Lock()
	defer m.Unlock()

	// Check if Client exists, then delete it
	if client, ok := m.clients[id]; ok {
		// close connection
		err := client.conn.Close()
		if err != nil {
			return
		}
		// remove
		delete(m.clients, id)
	}
}
