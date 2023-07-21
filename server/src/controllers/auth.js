const User = require("../models/User");
const jwt = require("jsonwebtoken");
const bcrypt = require("bcrypt");

async function signUp(req, res) {
    try {
        const { name, password } = req.body;

        const user = await User.findOne({ name });

        if (user === null) {
            let newUser = new User({
                name,
                password,
            });

            await newUser.save();

            return res.end();
        } else {
            return res.sendStatus(409).end();
        }
    } catch (error) {
        console.log(error);
    }
}

async function logIn(req, res) {
    const { name, password } = req.body;

    const user = await User.findOne({ name });

    if (user !== null) {
        let matches = await bcrypt.compare(password, user.password);

        if (matches) {
            const token = jwt.sign({ name }, process.env.JWT_SECRET);

            return res.json({ token }).end();
        } else {
            return res.sendStatus(401).end();
        }
    }

    return res.sendStatus(404).end();
}

module.exports = {
    signUp,
    logIn,
};
