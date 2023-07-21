require("dotenv").config();

const express = require("express");
const router = require("./router");
const bodyParser = require("body-parser");

const app = express();
const port = process.env.PORT || 8080;

app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ extended: true }));
app.use("/", router);

app.listen(port, () => {
    console.log(`app running on port ${port}`);
});
