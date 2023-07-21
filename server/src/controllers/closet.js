const jwt = require("jsonwebtoken");
const User = require("../models/User");

async function newClothes(req, res) {
    try {
        const token = req.header("authorization").split(" ")[1];
        const payload = jwt.verify(token, process.env.JWT_SECRET);

        if (payload.name !== null) {
            let user = await User.findOne({ name: payload.name });

            console.log(req.body)

            const { name, brand, image, type } = req.body;

            user.clothes.push({
                name,
                brand,
                type,
            });

            await user.save();

            return res.end();
        } else {
            return res.sendStatus(401).end();
        }
    } catch (error) {
        console.log(error);
    }
}

module.exports = {
    newClothes,
};
