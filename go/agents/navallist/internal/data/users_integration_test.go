//go:build integration

package data

import (
	"context"
	"testing"

	"github.com/charmbracelet/log"
)

func TestUserOperations(t *testing.T) {
	db := setupTestDB(t)
	defer func() {
		if err := db.Close(); err != nil {
			log.Error("failed to close database connection", "error", err)
		}
	}()

	store := NewSQLStore(db)
	ctx := context.Background()

	// Cleanup before and after
	cleanupData(t, db, "users")
	defer cleanupData(t, db, "users")

	// 1. Test GetOrCreateUser
	email := "test@example.com"
	sub := "sub123"
	name := "Test User"
	pic := "https://example.com/pic.jpg"

	user, err := store.GetOrCreateUser(ctx, email, sub, name, pic)
	if err != nil {
		t.Fatalf("GetOrCreateUser failed: %v", err)
	}
	if user.Email != email {
		t.Errorf("Expected email %s, got %s", email, user.Email)
	}

	// 2. Test GetUser
	fetchedUser, err := store.GetUser(ctx, user.ID)
	if err != nil {
		t.Fatalf("GetUser failed: %v", err)
	}
	if fetchedUser.ID != user.ID {
		t.Errorf("Expected ID %s, got %s", user.ID, fetchedUser.ID)
	}

	// 3. Test UpdateUser
	newName := "Updated Name"
	err = store.UpdateUser(ctx, user.ID, newName)
	if err != nil {
		t.Fatalf("UpdateUser failed: %v", err)
	}

	updatedUser, _ := store.GetUser(ctx, user.ID)
	if updatedUser.Name == nil || *updatedUser.Name != newName {
		t.Errorf("Expected name %s, got %v", newName, updatedUser.Name)
	}
}
