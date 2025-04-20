package control

import (
	"context"
	"fmt"
	"net/http"
	"time"
)

type contextKey string

const MiddlewareSentSession contextKey = "session"

func (c *Controller) AuthMiddleware(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		sessionTokenCookie, err := r.Cookie("session_token")
		fmt.Println("inside wathever")
		if err != nil {
			RespondWithError(w, http.StatusUnauthorized, err.Error())
			return
		}

		session, err := c.ValidateSession(r.Context(), sessionTokenCookie.Value)
		if err != nil {
			http.SetCookie(w, &http.Cookie{
				Name:     "session_token",
				Value:    "",
				Expires:  time.Now().Add(-time.Hour),
				HttpOnly: true,
			})

			RespondWithError(w, http.StatusUnauthorized, "Session expired")
			return
		}

		http.SetCookie(w, &http.Cookie{
			Name:     "session_token",
			Value:    sessionTokenCookie.Value,
			Expires:  time.Now().Add(time.Hour * 24 * 30),
			HttpOnly: true,
		})

		ctx := context.WithValue(r.Context(), MiddlewareSentSession, session)

		// fmt.Println("passed middleware check")

		next.ServeHTTP(w, r.WithContext(ctx))
	})
}
