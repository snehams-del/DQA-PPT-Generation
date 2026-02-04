package data

import (
	"context"
	"database/sql"
	"time"

	"navallist/internal/data/models"

	"github.com/charmbracelet/log"
)

// GetOrCreateUser retrieves a user by Google Subject ID or creates one if not exists.
func (s *SQLStore) GetOrCreateUser(ctx context.Context, email, googleSub, name, picture string) (*models.User, error) {
	user := &models.User{}
	query := `SELECT * FROM users WHERE google_sub = $1`
	err := s.db.GetContext(ctx, user, query, googleSub)

	if err == sql.ErrNoRows {
		// Create new user
		user.Email = email
		user.GoogleSub = googleSub
		user.Name = &name
		user.Picture = &picture
		user.CreatedAt = time.Now()

		insertQuery := `
			INSERT INTO users (email, google_sub, name, picture, created_at)
			VALUES (:email, :google_sub, :name, :picture, :created_at)
			RETURNING id`

		rows, err := s.db.NamedQueryContext(ctx, insertQuery, user)
		if err != nil {
			return nil, err
		}
		defer func() {
			if err := rows.Close(); err != nil {
				log.Error("failed to close rows", "error", err)
			}
		}()
		if rows.Next() {
			if err := rows.Scan(&user.ID); err != nil {
				return nil, err
			}
		}
		return user, nil
	} else if err != nil {
		return nil, err
	}

	return user, nil
}

// GetUser retrieves a user by ID.
func (s *SQLStore) GetUser(ctx context.Context, id string) (*models.User, error) {
	user := &models.User{}
	query := `SELECT * FROM users WHERE id = $1`
	err := s.db.GetContext(ctx, user, query, id)
	if err != nil {
		return nil, err
	}
	return user, nil
}

// FindUserByName retrieves a user by their name (case-insensitive).
func (s *SQLStore) FindUserByName(ctx context.Context, name string) (*models.User, error) {
	user := &models.User{}
	query := `SELECT * FROM users WHERE LOWER(name) = LOWER($1) LIMIT 1`
	err := s.db.GetContext(ctx, user, query, name)
	if err != nil {
		return nil, err
	}
	return user, nil
}

// UpdateUser updates the user's name.
func (s *SQLStore) UpdateUser(ctx context.Context, id, name string) error {
	query := `UPDATE users SET name = $1 WHERE id = $2`
	_, err := s.db.ExecContext(ctx, query, name, id)
	return err
}
