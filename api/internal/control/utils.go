package control

import (
	"context"
	"crypto/rand"
	"encoding/base64"
	"encoding/json"
	"errors"
	"log"
	"net/http"
	"time"

	"github.com/theAnuragMishra/decode-health/api/internal/database"
	"golang.org/x/crypto/bcrypt"
)

func RespondWithError(w http.ResponseWriter, code int, msg string) {
	if code > 499 {
		log.Println("Responding with 5XX error: ", msg)
	}

	type errResponse struct {
		Error string `json:"error"`
	}

	RespondWithJSON(w, code, errResponse{msg})
}

func RespondWithJSON(w http.ResponseWriter, code int, payload any) {
	data, err := json.Marshal(payload)
	if err != nil {
		log.Printf("Failed to marshal json response %v", err)
		w.WriteHeader(code)
		return
	}

	w.Header().Add("Content-Type", "application/json")
	w.WriteHeader(code)
	w.Write(data)
}

func hashPassword(password string) (string, error) {
	bytes, err := bcrypt.GenerateFromPassword([]byte(password), 14)
	return string(bytes), err
}

func checkPasswordHash(password, hash string) bool {
	err := bcrypt.CompareHashAndPassword([]byte(hash), []byte(password))
	return err == nil
}

func generateToken(length int) string {
	bytes := make([]byte, length)
	if _, err := rand.Read(bytes); err != nil {
		log.Fatalf("Failed to generate token: %v", err)
	}

	return base64.URLEncoding.EncodeToString(bytes)
}

func (c *Controller) ValidateSession(ctx context.Context, token string) (database.Session, error) {
	session, err := c.queries.GetSession(ctx, token)
	if err != nil {
		return session, errors.New("no such session")
	}
	if time.Now().After(session.ExpiresAt) {
		err := c.queries.DeleteSession(ctx, token)
		if err != nil {
			log.Println(err)
		}
		return session, errors.New("session expired")
	}
	if time.Now().Add(time.Hour * 24 * 15).After(session.ExpiresAt) {
		err := c.queries.UpdateSessionExpiry(ctx, database.UpdateSessionExpiryParams{
			ExpiresAt: time.Now().Add(time.Hour * 24 * 30),
			ID:        token,
		})
		if err != nil {
			log.Println("error updating session expiry, ", err)
		}
	}
	return session, nil
}
