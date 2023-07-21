const mongoose = require("mongoose");
const bcrypt = require("bcrypt");

const userSchema = mongoose.Schema({
    name: String,
    password: String,
    clothes: [
        {
            name: String,
            brand: String,
            image: String,
        },
    ],
});

userSchema.pre("save", function (next) {
    const user = this;

    if (user.password !== undefined) {
        bcrypt.hash(user.password, 10, (err, hashedPassword) => {
            if (err) console.log(err);

            this.password = hashedPassword;
            next();
        });
    }
});

const User = mongoose.model("user", userSchema, "users");

module.exports = User;
