const router = require("express").Router();
const path = require("path");
const { default: mongoose } = require("mongoose");
const { logIn, signUp } = require("./controllers/auth");
const { newClothes } = require("./controllers/closet");
const multer = require("multer");

mongoose.connect("mongodb://127.0.0.1:27017/outfit-designer");

const storage = multer.diskStorage({
    destination: (req, file, cb) => {
        cb(null, path.join(__dirname, "images"));
    },
    filename: (req, file, cb) => {
        const uniqueSufix = Date.now() + "-" + Math.round(Math.random() * 1e9);
        cb(null, file.fieldname + "-" + uniqueSufix);
    },
});
const upload = multer({ storage });

router.post("/sign-up", signUp);
router.post("/log-in", logIn);
router.post("/new-clothes", upload.single("image"), newClothes);

module.exports = router;
