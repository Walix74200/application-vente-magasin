function calculerPrixTotal() {
    var quantite = document.getElementById('quantite').value;
    var prixUnitaire = document.getElementById('prix_unitaire').value;
    var prixTotal = quantite * prixUnitaire;
    document.getElementById('prix_total').innerText = prixTotal.toFixed(2) + ' €';
}

// Exemple de script pour vérifier que le fichier JS est bien chargé
console.log('JavaScript chargé avec succès');
