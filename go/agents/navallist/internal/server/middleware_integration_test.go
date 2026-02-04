//go:build integration

package server

import (
	"context"
	"net/http"
	"net/http/httptest"
	"testing"

	"navallist/internal/config"
	"navallist/internal/data"

	"github.com/charmbracelet/log"
)

func TestAuthMiddleware(t *testing.T) {
	db := setupTestDB(t)
	defer func() {
		if err := db.Close(); err != nil {
			log.Error("failed to close database connection", "error", err)
		}
	}()

	store := data.NewSQLStore(db)
	srv := &Server{
		Store:  store,
		Config: &config.Config{},
	}

	// Create a user for auth
	user, err := store.GetOrCreateUser(context.Background(), "mid@test.com", "sub_mid", "Mid User", "pic")
	if err != nil {
		t.Fatalf("Failed to create user: %v", err)
	}
	defer db.Exec("DELETE FROM users WHERE id=$1", user.ID)

	// Dummy handler
	nextHandler := http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		w.WriteHeader(http.StatusOK)
		w.Write([]byte("Success"))
	})

	t.Run("Public Route", func(t *testing.T) {
		req := httptest.NewRequest("GET", "/", nil)
		w := httptest.NewRecorder()

		handler := srv.AuthMiddleware(AuthLevelPublic, nextHandler)
		handler.ServeHTTP(w, req)

		if w.Code != http.StatusOK {
			t.Errorf("Expected 200 OK, got %d", w.Code)
		}
	})

	t.Run("Private Route No Cookie", func(t *testing.T) {
		req := httptest.NewRequest("GET", "/", nil)
		w := httptest.NewRecorder()

		handler := srv.AuthMiddleware(AuthLevelUser, nextHandler)
		handler.ServeHTTP(w, req)

		if w.Code != http.StatusUnauthorized {
			t.Errorf("Expected 401 Unauthorized, got %d", w.Code)
		}
	})

	t.Run("Private Route Invalid Cookie", func(t *testing.T) {
		req := httptest.NewRequest("GET", "/", nil)
		req.AddCookie(&http.Cookie{Name: "user_session", Value: "invalid_id"})
		w := httptest.NewRecorder()

		handler := srv.AuthMiddleware(AuthLevelUser, nextHandler)
		handler.ServeHTTP(w, req)

		// Should fail because user lookup fails
		if w.Code != http.StatusUnauthorized {
			t.Errorf("Expected 401 Unauthorized, got %d", w.Code)
		}
	})

	t.Run("Private Route Valid Cookie", func(t *testing.T) {
		req := httptest.NewRequest("GET", "/", nil)
		req.AddCookie(&http.Cookie{Name: "user_session", Value: user.ID})
		w := httptest.NewRecorder()

		handler := srv.AuthMiddleware(AuthLevelUser, nextHandler)
		handler.ServeHTTP(w, req)

		if w.Code != http.StatusOK {
			t.Errorf("Expected 200 OK, got %d", w.Code)
		}
	})
}
