// =====================================================
// Script MongoDB - Gestion de la collection employes
// =====================================================

// 1️⃣ Compter le nombre de documents
print("Nombre de documents dans la collection employes :");
print(db.employes.countDocuments());

// 2️⃣ Insérer deux employés de deux manières différentes
// Méthode 1 : insertOne
db.employes.insertOne({
    nom: "Dupont",
    prenom: "David",
    prime: 1200
});

// Méthode 2 : insertMany
db.employes.insertMany([
    { nom: "Durand", prenom: "Denis", anciennete: 4 }
]);

// 3️⃣ Afficher la liste des employés dont le prénom est David
print("Employés dont le prénom est David :");
db.employes.find({ prenom: "David" }).pretty();

// 4️⃣ Afficher la liste des employés dont le prénom commence ou se termine par D
print("Employés dont le prénom commence ou se termine par D :");
db.employes.find({
    prenom: { $regex: "^D|D$", $options: "i" }
}).pretty();

// 5️⃣ Afficher la liste des employés dont le prénom commence par D et contient exactement 5 lettres
print("Employés dont le prénom commence par D et contient exactement 5 lettres :");
db.employes.find({
    prenom: { $regex: "^D.{4}$", $options: "i" }
}).pretty();

// 6️⃣ Afficher les nom et prénom des employés ayant une ancienneté > 10
print("Nom et prénom des employés avec ancienneté > 10 :");
db.employes.find(
    { anciennete: { $gt: 10 } },
    { _id: 0, nom: 1, prenom: 1 }
).pretty();

// 7️⃣ Afficher les nom et adresse complète des employés ayant un attribut rue
print("Nom et adresse des employés ayant un champ 'rue' :");
db.employes.find(
    { "adresse.rue": { $exists: true } },
    { _id: 0, nom: 1, adresse: 1 }
).pretty();

// 8️⃣ Incrémenter de 200 la prime des employés ayant déjà le champ prime
db.employes.updateMany(
    { prime: { $exists: true } },
    { $inc: { prime: 200 } }
);

// 9️⃣ Attribuer une prime de 1500 aux employés n'ayant pas de prime et dont la ville n'est pas Toulouse, Bordeaux, Paris
db.employes.updateMany(
    { 
        prime: { $exists: false },
        "adresse.ville": { $nin: ["Toulouse", "Bordeaux", "Paris"] }
    },
    { $set: { prime: 1500 } }
);

// 🔟 Créer un champ prime pour les documents qui n'en disposent pas et l'affecter à 100
db.employes.updateMany(
    { prime: { $exists: false } },
    { $set: { prime: 100 } }
);

// 1️⃣1️⃣ Ajouter un champ avec le nombre de caractères du nom de la ville
db.employes.updateMany(
    { "adresse.ville": { $exists: true } },
    [
        { $set: { nbCaractereVille: { $strLenCP: "$adresse.ville" } } }
    ]
);

// 1️⃣2️⃣ Calculer et afficher la somme de l'ancienneté pour les employés ayant le même prénom
print("Somme de l'ancienneté par prénom :");
db.employes.aggregate([
    { $group: { _id: "$prenom", totalAnciennete: { $sum: "$anciennete" } } }
]).forEach(printjson);
