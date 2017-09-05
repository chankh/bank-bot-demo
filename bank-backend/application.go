package main

import (
	"io/ioutil"
	"net/http"
	"net/url"
	"os"

	log "github.com/sirupsen/logrus"

	"gopkg.in/oauth2.v3/errors"
	"gopkg.in/oauth2.v3/manage"
	"gopkg.in/oauth2.v3/models"
	"gopkg.in/oauth2.v3/server"
	"gopkg.in/oauth2.v3/store"
	session "gopkg.in/session.v1"
)

var (
	globalSessions *session.Manager
)

func init() {
	globalSessions, _ = session.NewManager("memory", `{"cookieName":"gosessionid","gclifetime":3600}`)
	go globalSessions.GC()
}

func main() {
	port := os.Getenv("PORT")
	if port == "" {
		port = "5000"
	}

	redirect := os.Getenv("REDIRECT_URI")
	if redirect == "" {
		redirect = "http://localhost:5000/"
	}

	env := os.Getenv("ENV")
	if env == "PROD" {
		f, _ := os.OpenFile("/var/log/golang-server.log", os.O_WRONLY|os.O_CREATE, 0644)
		defer f.Close()
		log.SetOutput(f)
	} else {
		log.SetLevel(log.DebugLevel)
	}

	manager := manage.NewDefaultManager()
	// token memory store
	manager.MustTokenStorage(store.NewMemoryTokenStore())

	// client memory store
	clientStore := store.NewClientStore()
	clientStore.Set("000000", &models.Client{
		ID:     "000000",
		Secret: "999999",
		Domain: redirect,
	})
	manager.MapClientStorage(clientStore)

	srv := server.NewServer(server.NewConfig(), manager)
	srv.SetUserAuthorizationHandler(userAuthorizeHandler)

	srv.SetInternalErrorHandler(func(err error) (re *errors.Response) {
		log.Error("Internal Error:", err.Error())
		return
	})

	srv.SetResponseErrorHandler(func(re *errors.Response) {
		log.Error("Response Error:", re.Error.Error())
	})

	http.HandleFunc("/", indexHandler)
	http.HandleFunc("/login", loginHandler)
	http.HandleFunc("/auth", authHandler)

	http.HandleFunc("/authorize", func(w http.ResponseWriter, r *http.Request) {
		err := srv.HandleAuthorizeRequest(w, r)
		if err != nil {
			http.Error(w, err.Error(), http.StatusBadRequest)
		}
	})

	http.HandleFunc("/token", func(w http.ResponseWriter, r *http.Request) {
		err := srv.HandleTokenRequest(w, r)
		if err != nil {
			http.Error(w, err.Error(), http.StatusInternalServerError)
		}
	})

	http.HandleFunc("/accounts", accountsHandler)
	http.HandleFunc("/transfer", transferHandler)

	log.Infof("Listening on port %s", port)
	log.Fatal(http.ListenAndServe(":"+port, nil))
}

func userAuthorizeHandler(w http.ResponseWriter, r *http.Request) (userID string, err error) {
	us, err := globalSessions.SessionStart(w, r)
	uid := us.Get("UserID")
	if uid == nil {
		if r.Form == nil {
			r.ParseForm()
		}
		us.Set("Form", r.Form)
		w.Header().Set("Location", "/login")
		w.WriteHeader(http.StatusFound)
		return
	}
	userID = uid.(string)
	us.Delete("UserID")
	return
}

func indexHandler(w http.ResponseWriter, r *http.Request) {
	const indexPage = "public/index.html"
	if r.Method == "POST" {
		if buf, err := ioutil.ReadAll(r.Body); err == nil {
			log.Debugf("Received message: %s", string(buf))
		}
	} else {
		log.Debugf("Serving %s to %s...", indexPage, r.RemoteAddr)
		outputHTML(w, r, indexPage)
	}
}

func loginHandler(w http.ResponseWriter, r *http.Request) {
	if r.Method == "POST" {
		us, err := globalSessions.SessionStart(w, r)
		if err != nil {
			http.Error(w, err.Error(), http.StatusInternalServerError)
			return
		}
		us.Set("LoggedInUserID", "000000")
		w.Header().Set("Location", "/auth")
		w.WriteHeader(http.StatusFound)
		return
	}
	outputHTML(w, r, "public/login.html")
}

func authHandler(w http.ResponseWriter, r *http.Request) {
	us, err := globalSessions.SessionStart(w, r)
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}
	if us.Get("LoggedInUserID") == nil {
		w.Header().Set("Location", "/login")
		w.WriteHeader(http.StatusFound)
		return
	}
	if r.Method == "POST" {
		log.Printf("%+v", us.Get("Form"))
		form := us.Get("Form").(url.Values)
		u := new(url.URL)
		u.Path = "/authorize"
		u.RawQuery = form.Encode()
		w.Header().Set("Location", u.String())
		w.WriteHeader(http.StatusFound)
		us.Delete("Form")
		us.Set("UserID", us.Get("LoggedInUserID"))
		return
	}
	outputHTML(w, r, "public/auth.html")
}

func outputHTML(w http.ResponseWriter, req *http.Request, filename string) {
	file, err := os.Open(filename)
	if err != nil {
		http.Error(w, err.Error(), 500)
		return
	}
	defer file.Close()
	fi, _ := file.Stat()
	http.ServeContent(w, req, file.Name(), fi.ModTime(), file)
}
