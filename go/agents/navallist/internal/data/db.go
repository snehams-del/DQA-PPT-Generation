package data

import (
	"context"
	"log"
	"time"

	_ "github.com/jackc/pgx/v5/stdlib" // pgx driver
	"github.com/jmoiron/sqlx"
)

// SQLStore implements the Store interface using a PostgreSQL database.
type SQLStore struct {
	db *sqlx.DB
}

// NewSQLStore creates a new SQLStore with the given database connection.
func NewSQLStore(db *sqlx.DB) *SQLStore {
	return &SQLStore{db: db}
}

// TODO: Implement the actual ADK session.Service interface methods here.
// e.g. Create, Get, Update, etc.
// We need to know the exact signature to implement them correctly.

// CreateSession initializes a new ADK session.

func (s *SQLStore) CreateSession(_ context.Context, _ string) error {

	return nil

}

// GetSession retrieves an ADK session by ID.

func (s *SQLStore) GetSession(_ context.Context, _ string) (any, error) {

	return nil, nil

}

// DB returns the underlying sqlx.DB connection.
func (s *SQLStore) DB() *sqlx.DB {
	return s.db
}

// NewDB establishes a connection to the database.
func NewDB(dsn string) (*sqlx.DB, error) {
	db, err := sqlx.Connect("pgx", dsn)
	if err != nil {
		return nil, err
	}

	// Set some reasonable default connection pool settings
	db.SetMaxOpenConns(25)
	db.SetMaxIdleConns(5)
	db.SetConnMaxLifetime(5 * time.Minute)

	if err := db.Ping(); err != nil {
		return nil, err
	}

	log.Println("Database connection established")
	return db, nil
}
