package control

type signUpData struct {
	Name     string `json:"name"`
	Kind     string `json:"role"`
	Password string `json:"password"`
}

type loginData struct {
	ID       int32  `json:"id"`
	Password string `json:"password"`
}

type request struct {
	Name       string `json:"name"`
	Sequence   string `json:"sequence"`
	Age        int16  `json:"age"`
	HospitalID int32  `json:"hospitalID"`
	LabID      int32  `json:"labID"`
}

type reqID struct {
	ID int32 `json:"id"`
}

type report struct {
	Report string `json:"report"`
}
