package converter

import (
	"encoding/json"
	"log/slog"
	"time"
)

type VideoTask struct {
	VideoID int    `json:"video_id"`
	Path    string `json:"path"`
}

type VideoConverter struct{}

func (vc *VideoConverter) Handle(msg []byte) {
	var task VideoTask
	err := json.Unmarshal(msg, &task)

	if err != nil {
		vc.LogError(task, "Failed to unmarshall task", err)
	}
}

func (vc *VideoConverter) LogError(task VideoTask, msg string, err error) {
	errorData := map[string]any{
		"video_id": task.VideoID,
		"error":    msg,
		"details":  err.Error(),
		"time":     time.Now(),
	}

	serialized, _ := json.Marshal(errorData)
	// TODO: Deal with this error

	slog.Error("Processing error", slog.String("error_details", string(serialized)))

	// TODO: Register error on db
}
