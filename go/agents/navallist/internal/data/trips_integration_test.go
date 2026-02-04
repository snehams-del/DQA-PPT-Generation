//go:build integration

package data

import (
	"context"
	"testing"
	"time"

	"github.com/charmbracelet/log"
)

func TestTripOperations(t *testing.T) {
	db := setupTestDB(t)
	defer func() {
		if err := db.Close(); err != nil {
			log.Error("failed to close database connection", "error", err)
		}
	}()

	store := NewSQLStore(db)
	ctx := context.Background()

	// Cleanup before and after
	cleanupData(t, db, "trip", "users")
	defer cleanupData(t, db, "trip", "users")

	// 1. Create a User for the trip
	user, err := store.GetOrCreateUser(ctx, "captain@example.com", "sub123", "Captain", "pic.jpg")
	if err != nil {
		t.Fatalf("Failed to create user: %v", err)
	}

	// 2. Test GetOrCreateTrip (New)
	adkSession := "session_" + time.Now().Format("20060102150405")
	trip, err := store.GetOrCreateTrip(ctx, adkSession, user.ID, "Captain Jack", "Departing")
	if err != nil {
		t.Fatalf("GetOrCreateTrip failed: %v", err)
	}
	if trip.CaptainName == nil || *trip.CaptainName != "Captain Jack" {
		t.Errorf("Expected captain 'Captain Jack', got %v", trip.CaptainName)
	}
	if trip.Status != "Draft" {
		t.Errorf("Expected status 'Draft', got %s", trip.Status)
	}

	// 3. Test UpdateTripMetadata
	newBoat := "The Pearl"
	updatedTrip, err := store.UpdateTripMetadata(ctx, adkSession, &newBoat, nil)
	if err != nil {
		t.Fatalf("UpdateTripMetadata failed: %v", err)
	}
	if updatedTrip.BoatName == nil || *updatedTrip.BoatName != "The Pearl" {
		t.Errorf("Expected boat name 'The Pearl', got %v", updatedTrip.BoatName)
	}

	// 4. Test UpdateTripStatus
	err = store.UpdateTripStatus(ctx, trip.ID, "Ready")
	if err != nil {
		t.Fatalf("UpdateTripStatus failed: %v", err)
	}

	// Verify status update
	fetchedTrip, err := store.GetTrip(ctx, trip.ID)
	if err != nil {
		t.Fatalf("GetTrip failed: %v", err)
	}
	if fetchedTrip.Status != "Ready" {
		t.Errorf("Expected status 'Ready', got %s", fetchedTrip.Status)
	}

	// 5. Test ListUserTrips
	trips, err := store.ListUserTrips(ctx, user.ID)
	if err != nil {
		t.Fatalf("ListUserTrips failed: %v", err)
	}
	if len(trips) == 0 {
		t.Error("Expected at least one trip for user")
	}

	// 6. Test DeleteTrip
	err = store.DeleteTrip(ctx, trip.ID)
	if err != nil {
		t.Fatalf("DeleteTrip failed: %v", err)
	}

	_, err = store.GetTrip(ctx, trip.ID)
	if err == nil {
		t.Error("Expected error getting deleted trip, got nil")
	}
}
