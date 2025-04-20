package control

import (
	"encoding/json"
	"log"
	"net/http"
	"time"

	"github.com/theAnuragMishra/decode-health/api/internal/database"
)

func (c *Controller) SignUpHandler(w http.ResponseWriter, r *http.Request) {
	var payload signUpData
	err := json.NewDecoder(r.Body).Decode(&payload)
	if err != nil {
		RespondWithError(w, http.StatusBadRequest, "invalid request payload")
		return
	}
	passwordHash, err := hashPassword(payload.Password)
	if err != nil {
		RespondWithError(w, http.StatusInternalServerError, "server error")
	}
	err = c.queries.CreateOrg(r.Context(), database.CreateOrgParams{Name: payload.Name, Kind: payload.Kind, PasswordHash: passwordHash})
	if err != nil {
		RespondWithError(w, http.StatusInternalServerError, "error creating org")
		return
	}
	RespondWithJSON(w, http.StatusOK, "org created")
}

func (c *Controller) LoginHandler(w http.ResponseWriter, r *http.Request) {
	var payload loginData
	err := json.NewDecoder(r.Body).Decode(&payload)
	if err != nil {
		RespondWithError(w, http.StatusBadRequest, "bad request")
		return
	}
	org, err := c.queries.GetOrg(r.Context(), payload.ID)
	if err != nil || !checkPasswordHash(payload.Password, org.PasswordHash) {
		RespondWithError(w, http.StatusUnauthorized, "wrong password or userename")
		return
	}

	token := generateToken(32)
	http.SetCookie(w, &http.Cookie{
		Name:     "session_token",
		Value:    token,
		Expires:  time.Now().Add(time.Hour * 24 * 30),
		HttpOnly: true,
	})
	err = c.queries.CreateSession(r.Context(), database.CreateSessionParams{
		ID:        token,
		OrgID:     org.ID,
		ExpiresAt: time.Now().UTC().Add(24 * time.Hour * 30),
	})
	if err != nil {
		RespondWithError(w, http.StatusInternalServerError, "couldn't create session")
		return
	}
	RespondWithJSON(w, http.StatusOK, "signed in")
}

func (c *Controller) HandleLogout(w http.ResponseWriter, r *http.Request) {
	// fmt.Println("into handle logout")

	sessionTokenCookie, err := r.Cookie("session_token")
	if err != nil {
		RespondWithError(w, http.StatusInternalServerError, err.Error())
		return
	}

	http.SetCookie(w, &http.Cookie{
		Name:     "session_token",
		Value:    "",
		Expires:  time.Now().Add(-time.Hour),
		HttpOnly: true,
	})
	err = c.queries.DeleteSession(r.Context(), sessionTokenCookie.Value)
	if err != nil {
		log.Printf("error deleting session: %v", err)
		return
	}
}

func (c *Controller) HandleMe(w http.ResponseWriter, r *http.Request) {
	session := r.Context().Value(MiddlewareSentSession).(database.Session)

	org, err := c.queries.GetOrg(r.Context(), session.OrgID)
	if err != nil {
		RespondWithError(w, http.StatusInternalServerError, "Error getting user")
		return
	}

	RespondWithJSON(w, http.StatusOK, map[string]interface{}{"username": org.Name, "orgID": org.ID})
}

func (c *Controller) CreateRequest(w http.ResponseWriter, r *http.Request) {
	var req request
	err := json.NewDecoder(r.Body).Decode(&req)
	if err != nil {
		log.Println(err)
	}
	err = c.queries.CreateRequest(r.Context(), database.CreateRequestParams{
		Name:       req.Name,
		Sequence:   req.Sequence,
		HospitalID: req.HospitalID,
		LabID:      req.LabID,
		Age:        req.Age,
	})

	if err != nil {
		RespondWithError(w, http.StatusInternalServerError, "server error")
		return
	}
	RespondWithJSON(w, http.StatusOK, "success")
}

func (c *Controller) MarkRequestFulfilled(w http.ResponseWriter, r *http.Request) {
	var req reqID
	err := json.NewDecoder(r.Body).Decode(&req)
	if err != nil {
		RespondWithError(w, http.StatusBadRequest, "bad request")
		return
	}
	err = c.queries.MarkRequestFulfilled(r.Context(), req.ID)
	if err != nil {
		RespondWithError(w, http.StatusInternalServerError, "server error")
		return

	}

	RespondWithJSON(w, http.StatusOK, "success")
}

func (c *Controller) MarkRequestAccepted(w http.ResponseWriter, r *http.Request) {
	var req reqID
	err := json.NewDecoder(r.Body).Decode(&req)
	if err != nil {
		RespondWithError(w, http.StatusBadRequest, "bad request")
		return
	}
	err = c.queries.MarkRequestAccepted(r.Context(), req.ID)
	if err != nil {
		RespondWithError(w, http.StatusInternalServerError, "server error")
		return
	}
	RespondWithJSON(w, http.StatusOK, "success")
}

func (c *Controller) MarkRequestDenied(w http.ResponseWriter, r *http.Request) {
	var req reqID
	err := json.NewDecoder(r.Body).Decode(&req)
	if err != nil {
		RespondWithError(w, http.StatusBadRequest, "bad request")
		return
	}

}

func (c *Controller) DeleteRequest(w http.ResponseWriter, r *http.Request) {
	var req reqID
	err := json.NewDecoder(r.Body).Decode(&req)
	if err != nil {
		RespondWithError(w, http.StatusBadRequest, "bad request")
		return

	}
	err = c.queries.DeleteRequest(r.Context(), req.ID)
	if err != nil {
		RespondWithError(w, http.StatusInternalServerError, "server error")
		return
	}
	RespondWithJSON(w, http.StatusOK, "success")
}

func (c *Controller) GetRequestsForHospitals(w http.ResponseWriter, r *http.Request) {
	var id reqID
	err := json.NewDecoder(r.Body).Decode(&id)
	if err != nil {
		RespondWithError(w, http.StatusBadRequest, "bad request")
		return
	}
	requests, err := c.queries.GetRequestsForHospital(r.Context(), id.ID)

	if err != nil {
		RespondWithError(w, http.StatusInternalServerError, "server error")
		return
	}
	RespondWithJSON(w, http.StatusOK, requests)
}

func (c *Controller) GetRequestsForLab(w http.ResponseWriter, r *http.Request) {
	var id reqID
	err := json.NewDecoder(r.Body).Decode(&id)
	if err != nil {
		RespondWithError(w, http.StatusBadRequest, "bad request")
		return

	}
	requests, err := c.queries.GetRequestsForLab(r.Context(), id.ID)
	if err != nil {
		RespondWithError(w, http.StatusInternalServerError, "server error")
		return

	}
	RespondWithJSON(w, http.StatusOK, requests)

}

func (c *Controller) GetLabs(w http.ResponseWriter, r *http.Request) {
	labs, err := c.queries.GetLabs(r.Context())
	if err != nil {
		RespondWithError(w, http.StatusInternalServerError, "server error")
		return
	}
	RespondWithJSON(w, http.StatusOK, labs)

}
