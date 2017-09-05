package main

import "net/http"

const PROFILES = "{\"name\":{\"firstName\": \"JOHN\", \"lastName\": \"DOE\", \"nameType\": \"ENGLISH_NAME\", \"fullName\": \"JOHN DOE\"}, \"prefix\": \"MR\"}"

func profilesHandler(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")
	w.Write([]byte(PROFILES))
}
