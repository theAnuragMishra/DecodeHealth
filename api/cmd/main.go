package main

import (
	"context"
	"log"
	"net/http"
	"os"

	"github.com/go-chi/chi/v5"
	"github.com/jackc/pgx/v5/pgxpool"
	"github.com/joho/godotenv"
	"github.com/theAnuragMishra/decode-health/api/internal/control"
	"github.com/theAnuragMishra/decode-health/api/internal/database"
)

func main() {
	err := godotenv.Load()
	if err != nil {
		log.Fatal("error loading env")
	}

	setup()
}

func setup() {
	portString := os.Getenv("PORT")
	if portString == "" {
		log.Fatal("PORT not found")
	}

	dbURL := os.Getenv("PG_URL")
	if dbURL == "" {
		log.Fatal("DB_URL not found")
	}

	ctx := context.Background()

	pool, err := pgxpool.New(ctx, dbURL)
	if err != nil {
		log.Fatal("can't connect to database")
	}

	defer pool.Close()

	queries := database.New(pool)

	router := chi.NewRouter()

	controller := control.NewController(queries, router)
	controller.SetUpRouter()

	srv := &http.Server{
		Handler: router,
		Addr:    ":" + portString,
	}

	log.Printf("Server starting on port: %v", portString)
	err = srv.ListenAndServe()
	if err != nil {
		log.Fatal(err)
	}
}
