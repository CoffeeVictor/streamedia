package converter

import (
	"encoding/json"
	"fmt"
	"log/slog"
	"os"
	"os/exec"
	"path/filepath"
	"regexp"
	"sort"
	"strconv"
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

func (vc *VideoConverter) ProcessVideo(task *VideoTask) error {
	mergedFilePath := filepath.Join(task.Path, "merged.mp4")
	mpegDashPath := filepath.Join(task.Path, "mpeg-dash")

	slog.Info("Merging chunks", slog.String("path", task.Path))

	err := vc.mergeChunks(task.Path, mergedFilePath)

	if err != nil {
		vc.LogError(*task, "Failed to merge chunks", err)
		return err
	}

	slog.Info("Creating mpeg-dash dir", slog.String("path", task.Path))
	err = os.MkdirAll(mpegDashPath, os.ModePerm)

	if err != nil {
		vc.LogError(*task, "Failed to create mpeg-dash directory", err)
		return err
	}

	slog.Info("Converting video to mpeg-dash", slog.String("path", task.Path))
	ffmpegCmd := exec.Command("ffmpeg", "-i", mergedFilePath, "-f", "dash", filepath.Join(mpegDashPath, "output.mpd"))

	output, err := ffmpegCmd.CombinedOutput()

	if err != nil {
		vc.LogError(*task, "Failed to convert video to mpeg-dash, output"+string(output), err)
		return err
	}

	slog.Info("Video converted to mpeg-dash", slog.String("path", mpegDashPath))

	slog.Info("Removing merged file", slog.String("path", mergedFilePath))
	err = os.Remove(mergedFilePath)

	if err != nil {
		vc.LogError(*task, "Failed to remove merged file", err)
		return err
	}

	return nil
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

func (vc *VideoConverter) extractNumber(fileName string) int {
	re := regexp.MustCompile(`\d+`)
	numStr := re.FindString(filepath.Base(fileName))
	num, err := strconv.Atoi(numStr)

	if err != nil {
		return -1
	}

	return num
}

func (vc *VideoConverter) mergeChunks(inputDir, outputFile string) error {
	chunks, err := filepath.Glob(filepath.Join(inputDir, "*.chunk"))

	if err != nil {
		return fmt.Errorf("Failed to find chunks: %v", err)
	}

	sort.Slice(chunks, func(i, j int) bool {
		return vc.extractNumber(chunks[i]) < vc.extractNumber(chunks[j])
	})

	output, err := os.Create(outputFile)

	if err != nil {
		return fmt.Errorf("Failed to create output file: %v", err)
	}
	defer output.Close()

	for _, chunk := range chunks {
		input, err := os.Open(chunk)

		if err != nil {
			return fmt.Errorf("Failed to open chunk: %v", err)
		}

		_, err = output.ReadFrom(input)

		if err != nil {
			return fmt.Errorf("Failed to write chunk %s to merged file: %v", chunk, err)
		}
		input.Close()
	}
	return nil
}
