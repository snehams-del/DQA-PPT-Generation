//go:build integration

package handlers

import (
	"bytes"
	"context"
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"os"
	"testing"

	"navallist/internal/data"

	"github.com/charmbracelet/log"
	_ "github.com/jackc/pgx/v5/stdlib"
	"github.com/jmoiron/sqlx"
)

// setupTestDB connects to the test database and returns the connection.
// Duplicated here to avoid circular imports or exported helpers in data if not desired.
// Ideally, we'd have a shared 'testutils' package, but this is fine for now.
func setupTestDB(t *testing.T) *sqlx.DB {
	t.Helper()
	dsn := os.Getenv("NAVALLIST_DB_CONNECTION_STRING")
	if dsn == "" {
		dsn = "postgres://navallist_user:password@localhost:5432/navallistdb?sslmode=disable"
	}
	db, err := sqlx.Connect("pgx", dsn)
	if err != nil {
		t.Skipf("Skipping integration test: %v", err)
	}
	return db
}

func TestTripsHandler(t *testing.T) {
	db := setupTestDB(t)
	defer func() {
		if err := db.Close(); err != nil {
			log.Error("failed to close database connection", "error", err)
		}
	}()

	store := data.NewSQLStore(db)
	h := NewTripsHandler(store, nil, nil)
	ctx := context.Background()

	// Cleanup
	db.Exec("DELETE FROM trip")
	db.Exec("DELETE FROM users")
	defer db.Exec("DELETE FROM trip")
	defer db.Exec("DELETE FROM users")

	// Create a user for auth context
	user, err := store.GetOrCreateUser(ctx, "handler@test.com", "sub_handler", "Handler User", "pic")
	if err != nil {
		t.Fatalf("Failed to create test user: %v", err)
	}

	// Helper to add cookie
	addAuthCookie := func(req *http.Request) {
		req.AddCookie(&http.Cookie{
			Name:  "user_session",
			Value: user.ID,
		})
	}

	t.Run("CreateTrip", func(t *testing.T) {
		body := map[string]string{
			"session_id":   "sess_123",
			"captain_name": "Capt. Test",
		}
		jsonBody, _ := json.Marshal(body)
		req := httptest.NewRequest("POST", "/api/trips", bytes.NewBuffer(jsonBody))
		addAuthCookie(req)
		w := httptest.NewRecorder()

		h.CreateTrip(w, req)

		if w.Code != http.StatusOK {
			t.Errorf("Expected 200 OK, got %d: %s", w.Code, w.Body.String())
		}

		var resp map[string]interface{}
		json.Unmarshal(w.Body.Bytes(), &resp)
		if resp["adk_session_id"] != "sess_123" {
			t.Errorf("Expected session_id sess_123, got %v", resp["adk_session_id"])
		}
	})

	t.Run("ListTrips", func(t *testing.T) {
		// Ensure a trip exists
		store.GetOrCreateTrip(ctx, "sess_list", user.ID, "List Capt", "Departing")

		req := httptest.NewRequest("GET", "/api/trips", nil)
		addAuthCookie(req)
		w := httptest.NewRecorder()

		h.ListTrips(w, req)

		if w.Code != http.StatusOK {
			t.Errorf("Expected 200 OK, got %d", w.Code)
		}
		var trips []map[string]interface{}
		json.Unmarshal(w.Body.Bytes(), &trips)
		if len(trips) == 0 {
			t.Error("Expected at least one trip")
		}
	})

	// Create a trip for specific ID tests
	trip, _ := store.GetOrCreateTrip(ctx, "sess_update", user.ID, "Update Capt", "Departing")

	t.Run("UpdateStatus", func(t *testing.T) {
		body := map[string]string{"status": "Ready"}
		jsonBody, _ := json.Marshal(body)

		req := httptest.NewRequest("PUT", "/api/trips/"+trip.ID+"/status", bytes.NewBuffer(jsonBody))
		req.SetPathValue("id", trip.ID) // Go 1.22+ routing feature
		addAuthCookie(req)
		w := httptest.NewRecorder()

		h.UpdateStatus(w, req)

		if w.Code != http.StatusOK {
			t.Errorf("Expected 200 OK, got %d", w.Code)
		}

		updated, _ := store.GetTrip(ctx, trip.ID)
		if updated.Status != "Ready" {
			t.Errorf("Expected status Ready, got %s", updated.Status)
		}
	})

	t.Run("GetTrip", func(t *testing.T) {
		req := httptest.NewRequest("GET", "/api/trips/"+trip.ID, nil)
		req.SetPathValue("id", trip.ID)
		addAuthCookie(req)
		w := httptest.NewRecorder()

		h.GetTrip(w, req)

		if w.Code != http.StatusOK {
			t.Errorf("Expected 200 OK, got %d", w.Code)
		}
	})

	t.Run("UpdateItem", func(t *testing.T) {
		// Need to add an item first? Or UpdateItem handles creation?
		// data.UpdateChecklistItem handles creation.

		body := map[string]interface{}{
			"is_checked":        true,
			"location":          "Deck",
			"photo_artifact_id": "art_123",
		}
		jsonBody, _ := json.Marshal(body)

		itemName := "Fenders"
		req := httptest.NewRequest("PUT", "/api/trips/"+trip.ID+"/items/"+itemName, bytes.NewBuffer(jsonBody))
		req.SetPathValue("id", trip.ID)
		req.SetPathValue("itemId", itemName)
		addAuthCookie(req)
		w := httptest.NewRecorder()

		h.UpdateItem(w, req)

		if w.Code != http.StatusOK {
			t.Errorf("Expected 200 OK, got %d: %s", w.Code, w.Body.String())
		}

		// Verify in DB
		items, _ := store.GetTripReport(ctx, trip.ID)
		found := false
		for _, i := range items {
			if i.Name == itemName && i.IsChecked {
				if i.CompletedByUserID != nil && *i.CompletedByUserID == user.ID {
					found = true
				}
				break
			}
		}
		if !found {
			t.Error("Item not updated/created in DB")
		}
	})
}
